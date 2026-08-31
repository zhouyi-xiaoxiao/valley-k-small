#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-replay-h3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=24:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail; umask 077; export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -eq 9 ]] || exit 2; PAYLOAD_SHA="$1"; RUN_TOKEN="$2"; ARRAY_JOB="$3"; REDUCER_JOB="$4"; REDUCTION_SHA="$5"; PRODUCTION_SUBMIT="$6"; PRODUCTION_SUBMIT_SHA="$7"; REDUCER_SUBMIT="$8"; REDUCER_SUBMIT_SHA="$9"; [[ "$RUN_TOKEN" == "$ARRAY_JOB" && "$ARRAY_JOB" =~ ^[0-9]+$ && "$REDUCER_JOB" =~ ^[0-9]+$ ]] || exit 2
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727; CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
module load cray-python/3.11.7; HOST_PYTHON="$(command -v python3)"; HOST_VERSION="$("$HOST_PYTHON" -c 'import platform; print(platform.python_version())')"; [[ "$HOST_VERSION" == 3.11.7 && ":${LOADEDMODULES:-}:" == *":cray-python/3.11.7:"* ]] || exit 2
cd "$ROOT"; printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h3_payload.sha256 | sha256sum -c - >/dev/null; sha256sum -c notes/isambard_ai_v4_r2_h3_payload.sha256 >/dev/null; printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
RUNTIME="$ROOT/artifacts/runtime_h3/replay-${SLURM_JOB_ID:?}.json"; mkdir -p "$ROOT/artifacts/runtime_h3"; chmod 700 "$ROOT/artifacts/runtime_h3"; apptainer exec "$CONTAINER" python3 code/runtime_probe_v4_r2_h3.py --phase replay --job-id "$SLURM_JOB_ID" --host-python-executable "$HOST_PYTHON" --host-python-version "$HOST_VERSION" --loaded-modules "${LOADEDMODULES:-}" --container "$CONTAINER" --output "$RUNTIME"
OUT="$ROOT/artifacts/replay/v4-r2-replay-h3-$REDUCER_JOB.json"; apptainer exec "$CONTAINER" python3 code/independent_replay_gpu_gating_v4_r2_h3.py --run-token "$RUN_TOKEN" --array-job "$ARRAY_JOB" --reducer-job "$REDUCER_JOB" --reduction-sha256 "$REDUCTION_SHA" --h3-payload-sha256 "$PAYLOAD_SHA" --production-submit "$PRODUCTION_SUBMIT" --production-submit-sha256 "$PRODUCTION_SUBMIT_SHA" --reducer-submit "$REDUCER_SUBMIT" --reducer-submit-sha256 "$REDUCER_SUBMIT_SHA" --output "$OUT"
