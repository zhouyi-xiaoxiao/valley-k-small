#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-combined
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=04:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727/logs/%x-%j.err

set -euo pipefail
umask 077
export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -eq 6 ]] || { echo "usage: combined PAYLOAD_SHA V3_JSON V3_CSV V4_JSON V4_CSV RUN_TOKEN" >&2; exit 2; }
PAYLOAD_SHA="$1" V3_JSON="$2" V3_CSV="$3" V4_JSON="$4" V4_CSV="$5" RUN_TOKEN="$6"
ROOT="/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727"
[[ "${PAYLOAD_SHA}" =~ ^[0-9a-f]{64}$ && "${RUN_TOKEN}" =~ ^[0-9]+$ ]] || exit 2
cd "${ROOT}"
printf '%s  %s\n' "${PAYLOAD_SHA}" notes/isambard_ai_v4_payload.sha256 | sha256sum -c - >/dev/null
sha256sum -c notes/isambard_ai_v4_payload.sha256 >/dev/null
for input in "${V3_JSON}" "${V3_CSV}" "${V4_JSON}" "${V4_CSV}"; do [[ -f "${input}" && ! -L "${input}" ]] || exit 3; done
OUT="${ROOT}/artifacts/outputs/isambard_ai_v4/combined-${RUN_TOKEN}-${SLURM_JOB_ID:?missing job id}"
mkdir -m 700 "${OUT}"
srun --ntasks=1 python3 code/analyze_gpu_gating_v4_combined.py \
  --v3-json "${V3_JSON}" --v3-csv "${V3_CSV}" --v4-json "${V4_JSON}" --v4-csv "${V4_CSV}" \
  --output-json "${OUT}/combined_v3_v4_max_t.json" --output-csv "${OUT}/combined_v3_v4_max_t.csv"
