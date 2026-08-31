#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v3-cell
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-gpu=8
#SBATCH --mem=32G
#SBATCH --time=00:20:00
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
GLOBAL_START="${4:?missing global cell-id start}"
RUN_TOKEN="${5:?missing shared run token}"
LOCAL_TASK_ID="${SLURM_ARRAY_TASK_ID:?this script must be launched as an array}"

case "${GLOBAL_START}" in
  ''|*[!0-9]*) echo "global start must contain decimal digits only" >&2; exit 2 ;;
esac
case "${RUN_TOKEN}" in
  ''|*[!0-9]*) echo "run token must contain decimal digits only" >&2; exit 2 ;;
esac
case "${LOCAL_TASK_ID}" in
  ''|*[!0-9]*) echo "local array task id must contain decimal digits only" >&2; exit 2 ;;
esac
CELL_ID=$((10#${GLOBAL_START} + 10#${LOCAL_TASK_ID}))

REPORT_ROOT="${SLURM_SUBMIT_DIR:?missing SLURM_SUBMIT_DIR}"
SCRIPT_DIR="${REPORT_ROOT}/code"
CONTAINER="/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
MANIFEST="${REPORT_ROOT}/${MANIFEST_RELATIVE}"
FIELD_PACK="${REPORT_ROOT}/${FIELD_PACK_RELATIVE}"
RESULT_DIR="${REPORT_ROOT}/artifacts/outputs/isambard_ai_v3/${PHASE}-${RUN_TOKEN}/cell-${CELL_ID}"
OUTPUT_JSON="${RESULT_DIR}/cell-${CELL_ID}.json"
OUTPUT_NPZ="${RESULT_DIR}/cell-${CELL_ID}.npz"
TASK_TMP="/tmp/valley-gating-v3-${RUN_TOKEN}-${SLURM_JOB_ID}-${CELL_ID}"

case "${MANIFEST_RELATIVE}" in
  /*|*../*|../*|*/..) echo "manifest path escaped report root" >&2; exit 2 ;;
esac
case "${FIELD_PACK_RELATIVE}" in
  /*|*../*|../*|*/..) echo "field-pack path escaped report root" >&2; exit 2 ;;
esac
case "${PHASE}" in
  canary)
    [[ "${GLOBAL_START}" == 0 && "${LOCAL_TASK_ID}" -le 7 ]] || {
      echo "canary requires global start 0 and local task 0..7" >&2
      exit 2
    }
    ;;
  production)
    echo "production phase must use isambard_ai_gating_v3_bundle.sbatch" >&2
    exit 2
    ;;
  tail160k)
    [[ "${GLOBAL_START}" == 0 && "${LOCAL_TASK_ID}" -le 383 ]] || {
      echo "tail160k requires global start 0 and local task 0..383" >&2
      exit 2
    }
    ;;
  recovery)
    [[ "${LOCAL_TASK_ID}" -le 479 && "${CELL_ID}" -le 5759 ]] || {
      echo "recovery cell is outside 0..5759" >&2
      exit 2
    }
    ;;
  *) echo "unrecognised phase label: ${PHASE}" >&2; exit 2 ;;
esac

mkdir -m 700 "${TASK_TMP}"
export TMPDIR="${TASK_TMP}"
cd "${REPORT_ROOT}"
sha256sum -c notes/isambard_ai_v3_payload.sha256 >/dev/null
mkdir -p "${RESULT_DIR}"

srun --ntasks=1 apptainer exec --nv "${CONTAINER}" \
  python3 "${SCRIPT_DIR}/gpu_gating_mc_v3.py" \
  --manifest "${MANIFEST}" \
  --field-pack "${FIELD_PACK}" \
  --cell-id "${CELL_ID}" \
  --device cuda \
  --output-json "${OUTPUT_JSON}" \
  --output-npz "${OUTPUT_NPZ}"
