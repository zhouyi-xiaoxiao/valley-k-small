#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v3-bundle
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-gpu=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --no-requeue
#SBATCH --output=logs/%x-%A_%a.out
#SBATCH --error=logs/%x-%A_%a.err

set -euo pipefail
umask 077
export LC_ALL=C
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

MANIFEST_RELATIVE="${1:?missing manifest path relative to the report root}"
FIELD_PACK_RELATIVE="${2:?missing field-pack path relative to the report root}"
PHASE="${3:?missing phase label}"
RUN_TOKEN="${4:?missing shared run token}"
LOCAL_TASK_ID="${SLURM_ARRAY_TASK_ID:?this script must be launched as an array}"

case "${MANIFEST_RELATIVE}" in
  /*|*../*|../*|*/..) echo "manifest path escaped report root" >&2; exit 2 ;;
esac
case "${FIELD_PACK_RELATIVE}" in
  /*|*../*|../*|*/..) echo "field-pack path escaped report root" >&2; exit 2 ;;
esac
case "${RUN_TOKEN}" in
  ''|*[!0-9]*) echo "run token must contain decimal digits only" >&2; exit 2 ;;
esac
case "${LOCAL_TASK_ID}" in
  ''|*[!0-9]*) echo "local array task id must contain decimal digits only" >&2; exit 2 ;;
esac
[[ "${PHASE}" == "production" ]] || {
  echo "bundled runner accepts production phase only" >&2
  exit 2
}
[[ "${LOCAL_TASK_ID}" -le 479 ]] || {
  echo "bundled production local task must be in 0..479" >&2
  exit 2
}

REPORT_ROOT="${SLURM_SUBMIT_DIR:?missing SLURM_SUBMIT_DIR}"
SCRIPT_DIR="${REPORT_ROOT}/code"
CONTAINER="/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
MANIFEST="${REPORT_ROOT}/${MANIFEST_RELATIVE}"
FIELD_PACK="${REPORT_ROOT}/${FIELD_PACK_RELATIVE}"
RESULT_ROOT="${REPORT_ROOT}/artifacts/outputs/isambard_ai_v3/${PHASE}-${RUN_TOKEN}"
TASK_TMP="/tmp/valley-gating-v3-bundle-${RUN_TOKEN}-${SLURM_JOB_ID}-${LOCAL_TASK_ID}"

mkdir -m 700 "${TASK_TMP}"
export TMPDIR="${TASK_TMP}"
cd "${REPORT_ROOT}"
sha256sum -c notes/isambard_ai_v3_payload.sha256 >/dev/null
[[ -f "${MANIFEST}" ]] || { echo "manifest does not exist: ${MANIFEST}" >&2; exit 2; }
[[ -f "${FIELD_PACK}" ]] || { echo "field pack does not exist: ${FIELD_PACK}" >&2; exit 2; }

# One allocation owns exactly twelve globally separated manifest cells.  Any
# failed cell terminates this allocation nonzero, so the afterok full reducer
# cannot run on a partial bundle.
for bundle_index in $(seq 0 11); do
  cell_id=$((10#${LOCAL_TASK_ID} + 480 * bundle_index))
  [[ "${cell_id}" -le 5759 ]] || { echo "computed cell id escaped 0..5759" >&2; exit 2; }
  result_dir="${RESULT_ROOT}/cell-${cell_id}"
  output_json="${result_dir}/cell-${cell_id}.json"
  output_npz="${result_dir}/cell-${cell_id}.npz"
  mkdir -p "${result_dir}"
  srun --ntasks=1 apptainer exec --nv "${CONTAINER}" \
    python3 "${SCRIPT_DIR}/gpu_gating_mc_v3.py" \
    --manifest "${MANIFEST}" \
    --field-pack "${FIELD_PACK}" \
    --cell-id "${cell_id}" \
    --device cuda \
    --output-json "${output_json}" \
    --output-npz "${output_npz}"
done
