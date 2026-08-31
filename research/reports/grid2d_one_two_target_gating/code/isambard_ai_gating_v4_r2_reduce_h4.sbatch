#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-reduce-h4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=06:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail
umask 077
export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -eq 7 ]] || exit 2
PAYLOAD_SHA="$1"; ARRAY_JOB="$2"; RUN_TOKEN="$3"; CANARY="$4"; CANARY_SHA="$5"; PRODUCTION_SUBMIT="$6"; PRODUCTION_SUBMIT_SHA="$7"
[[ "$ARRAY_JOB" =~ ^[0-9]+$ && "$RUN_TOKEN" == "$ARRAY_JOB" ]] || exit 2
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
module load cray-python/3.11.7
HOST_PYTHON="$(command -v python3)"
HOST_VERSION="$("$HOST_PYTHON" -c 'import platform; print(platform.python_version())')"
[[ "$HOST_VERSION" == 3.11.7 && ":${LOADEDMODULES:-}:" == *":cray-python/3.11.7:"* ]] || exit 2
cd "$ROOT"
printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h4_payload.sha256 | sha256sum -c - >/dev/null
sha256sum -c notes/isambard_ai_v4_r2_h4_payload.sha256 >/dev/null
printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
printf '%s  %s\n' "$CANARY_SHA" "$CANARY" | sha256sum -c - >/dev/null
printf '%s  %s\n' "$PRODUCTION_SUBMIT_SHA" "$PRODUCTION_SUBMIT" | sha256sum -c - >/dev/null
RUNTIME="$ROOT/artifacts/runtime_h4/reducer-${SLURM_JOB_ID:?}.json"
mkdir -p "$ROOT/artifacts/runtime_h4"; chmod 700 "$ROOT/artifacts/runtime_h4"
apptainer exec "$CONTAINER" python3 code/runtime_probe_v4_r2_h4.py --phase reducer --job-id "$SLURM_JOB_ID" --host-python-executable "$HOST_PYTHON" --host-python-version "$HOST_VERSION" --loaded-modules "${LOADEDMODULES:-}" --container "$CONTAINER" --output "$RUNTIME"
OUT="$ROOT/artifacts/outputs/isambard_ai_v4_r2/reduction-$RUN_TOKEN-${SLURM_JOB_ID:?}"
mkdir -m 700 "$OUT"
SACCT="$OUT/sacct-v4-r2-$ARRAY_JOB.psv"
sacct -X --array -j "$ARRAY_JOB" --format=JobIDRaw,JobID,ArrayJobID,ArrayTaskID,State,ExitCode,ElapsedRaw,AllocTRES,ReqTRES,NNodes --parsable2 > "$SACCT"
chmod 600 "$SACCT"
apptainer exec "$CONTAINER" python3 code/reduce_gpu_gating_v4_r2.py --mode full --manifest artifacts/data/gating_v4_r2_production_manifest.json --field-pack artifacts/data/disorder_field_pack_v4_r2_reflect.npz --results-dir "artifacts/outputs/isambard_ai_v4_r2/production-$RUN_TOKEN" --source code/gpu_gating_mc_v4_r2.py --sacct-receipt "$SACCT" --output-json "$OUT/reduction_v4_r2.json" --output-csv "$OUT/reduction_v4_r2.csv"
