#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-reduce
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
[[ "$#" -eq 3 ]] || { echo "usage: reducer PAYLOAD_SHA ARRAY_JOB_ID RUN_TOKEN" >&2; exit 2; }
PAYLOAD_SHA="$1" ARRAY_JOB_ID="$2" RUN_TOKEN="$3"
[[ "${PAYLOAD_SHA}" =~ ^[0-9a-f]{64}$ && "${ARRAY_JOB_ID}" =~ ^[0-9]+$ && "${RUN_TOKEN}" =~ ^[0-9]+$ ]] || exit 2
ROOT="/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-20260727"
RESULTS="${ROOT}/artifacts/outputs/isambard_ai_v4/production-${RUN_TOKEN}"
OUT="${ROOT}/artifacts/outputs/isambard_ai_v4/reduction-${RUN_TOKEN}-${SLURM_JOB_ID:?missing job id}"
mkdir -m 700 "${OUT}"
cd "${ROOT}"
printf '%s  %s\n' "${PAYLOAD_SHA}" notes/isambard_ai_v4_payload.sha256 | sha256sum -c - >/dev/null
sha256sum -c notes/isambard_ai_v4_payload.sha256 >/dev/null
sacct -X --array -j "${ARRAY_JOB_ID}" --starttime 2026-07-27 --format=JobIDRaw,JobID,State,ExitCode --parsable2 > "${OUT}/sacct-v4-${ARRAY_JOB_ID}.psv"
srun --ntasks=1 python3 code/reduce_gpu_gating_v4.py --mode full \
  --manifest artifacts/data/gating_v4_production_manifest.json \
  --field-pack artifacts/data/disorder_field_pack_v4.npz --results-dir "${RESULTS}" \
  --source code/gpu_gating_mc_v4.py --sacct-receipt "${OUT}/sacct-v4-${ARRAY_JOB_ID}.psv" \
  --output-json "${OUT}/reduction_v4.json" --output-csv "${OUT}/reduction_v4.csv"
