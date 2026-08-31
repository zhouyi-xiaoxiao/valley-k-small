#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-fullnode
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --gpus=4
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=02:00:00
#SBATCH --array=0-479%240
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727/logs/%x-%A_%a.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727/logs/%x-%A_%a.err

set -euo pipefail
umask 077
export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1

[[ "$#" -eq 4 ]] || { echo "usage: sbatch script PAYLOAD_SHA V3_REDUCTION_JSON V3_SECONDARY_JSON RUN_TOKEN" >&2; exit 2; }
PAYLOAD_SHA="$1"
V3_REDUCTION_JSON="$2"
V3_SECONDARY_JSON="$3"
RUN_TOKEN="$4"
[[ "${PAYLOAD_SHA}" =~ ^[0-9a-f]{64}$ ]] || { echo "invalid payload SHA" >&2; exit 2; }
[[ "${RUN_TOKEN}" =~ ^[0-9]+$ ]] || { echo "invalid run token" >&2; exit 2; }

ROOT="/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727"
MANIFEST="${ROOT}/artifacts/data/gating_v4_production_manifest.json"
PACK="${ROOT}/artifacts/data/disorder_field_pack_v4.npz"
PAYLOAD="${ROOT}/notes/isambard_ai_v4_payload.sha256"
CONTAINER="/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
RESULT_ROOT="${ROOT}/artifacts/outputs/isambard_ai_v4/production-${RUN_TOKEN}"
TASK_ID="${SLURM_ARRAY_TASK_ID:?missing array task}"

[[ "${SLURM_SUBMIT_DIR:?missing submit dir}" == "${ROOT}" ]] || { echo "wrong append-only root" >&2; exit 2; }
cd "${ROOT}"
printf '%s  %s\n' "${PAYLOAD_SHA}" "notes/isambard_ai_v4_payload.sha256" | sha256sum -c - >/dev/null
sha256sum -c "${PAYLOAD}" >/dev/null
for file in "${MANIFEST}" "${PACK}" "${CONTAINER}" "${V3_REDUCTION_JSON}" "${V3_SECONDARY_JSON}"; do
  [[ -f "${file}" && ! -L "${file}" ]] || { echo "missing or symlinked gate/input: ${file}" >&2; exit 3; }
done
python3 - "${V3_REDUCTION_JSON}" "${V3_SECONDARY_JSON}" <<'PY'
import json, pathlib, sys
primary = json.loads(pathlib.Path(sys.argv[1]).read_text())
secondary = json.loads(pathlib.Path(sys.argv[2]).read_text())
if primary.get("audit", {}).get("pass") is not True or primary.get("audit", {}).get("sacct", {}).get("verified") is not True:
    raise SystemExit("v3 primary integrity/audit gate is not PASS")
if secondary.get("status") != "PASS_SECONDARY_MAX_T_R1":
    raise SystemExit("v3 secondary max-t gate is not PASS")
PY
python3 code/validate_gating_campaign_manifest_v4.py --manifest "${MANIFEST}" --field-pack "${PACK}" >/dev/null

run_lane() {
  local lane="$1" k cell result_dir tmpdir
  tmpdir="/tmp/vk-gating-v4-${RUN_TOKEN}-${SLURM_JOB_ID}-${TASK_ID}-${lane}"
  mkdir -m 700 "${tmpdir}"
  for k in $(seq 0 11); do
    cell=$((10#${TASK_ID} + 480 * (10#${lane} + 4 * k)))
    [[ "${cell}" -ge 0 && "${cell}" -le 23039 ]] || return 91
    result_dir="${RESULT_ROOT}/cell-${cell}"
    mkdir -p "${result_dir}"
    TMPDIR="${tmpdir}" srun --exclusive --ntasks=1 --gpus-per-task=1 --cpus-per-task=8 --gpu-bind=single:1 \
      apptainer exec --nv "${CONTAINER}" python3 code/gpu_gating_mc_v4.py \
      --manifest "${MANIFEST}" --field-pack "${PACK}" --cell-id "${cell}" --device cuda \
      --output-json "${result_dir}/cell-${cell}.json" --output-npz "${result_dir}/cell-${cell}.npz" || return $?
  done
}

pids=()
for lane in 0 1 2 3; do run_lane "${lane}" & pids+=("$!"); done
status=0
set +e
for pid in "${pids[@]}"; do wait "${pid}" || status=1; done
set -e
[[ "${status}" -eq 0 ]] || { echo "one or more GPU lanes failed" >&2; exit 4; }

# Allocation-local completeness gate: exactly its 48 preregistered cells.
for lane in 0 1 2 3; do
  for k in $(seq 0 11); do
    cell=$((10#${TASK_ID} + 480 * (lane + 4 * k)))
    [[ -s "${RESULT_ROOT}/cell-${cell}/cell-${cell}.json" && -s "${RESULT_ROOT}/cell-${cell}/cell-${cell}.npz" ]] || exit 5
  done
done
