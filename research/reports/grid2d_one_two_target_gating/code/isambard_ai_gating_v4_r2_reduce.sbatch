#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-reduce
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=06:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail;umask 077;export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -eq 5 ]]||exit 2;PAYLOAD_SHA="$1";ARRAY_JOB="$2";RUN_TOKEN="$3";CANARY_RECEIPT="$4";CANARY_SHA="$5";[[ "$ARRAY_JOB" =~ ^[0-9]+$ && "$RUN_TOKEN" =~ ^[0-9]+$ ]]||exit 2
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727;CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif;CONTAINER_SHA=aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4
cd "$ROOT";printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_payload.sha256|sha256sum -c - >/dev/null;sha256sum -c notes/isambard_ai_v4_r2_payload.sha256 >/dev/null;printf '%s  %s\n' "$CONTAINER_SHA" "$CONTAINER"|sha256sum -c - >/dev/null;printf '%s  %s\n' "$CANARY_SHA" "$CANARY_RECEIPT"|sha256sum -c - >/dev/null
python3 - "$CANARY_RECEIPT" <<'PY'
import json,sys
assert json.load(open(sys.argv[1]))["status"]=="PASS_AUTHORIZE_V4_R2_PRODUCTION"
PY
OUT="$ROOT/artifacts/outputs/isambard_ai_v4_r2/reduction-$RUN_TOKEN-${SLURM_JOB_ID:?}";mkdir -m 700 "$OUT";SACCT="$OUT/sacct-v4-r2-$ARRAY_JOB.psv"
sacct -X --array -j "$ARRAY_JOB" --format=JobIDRaw,JobID,ArrayJobID,ArrayTaskID,State,ExitCode,ElapsedRaw,AllocTRES,ReqTRES,NNodes --parsable2 > "$SACCT"
python3 code/reduce_gpu_gating_v4_r2.py --mode full --manifest artifacts/data/gating_v4_r2_production_manifest.json --field-pack artifacts/data/disorder_field_pack_v4_r2_reflect.npz --results-dir "artifacts/outputs/isambard_ai_v4_r2/production-$RUN_TOKEN" --source code/gpu_gating_mc_v4_r2.py --sacct-receipt "$SACCT" --output-json "$OUT/reduction_v4_r2.json" --output-csv "$OUT/reduction_v4_r2.csv"
