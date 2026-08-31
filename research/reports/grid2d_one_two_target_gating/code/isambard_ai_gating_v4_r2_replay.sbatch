#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-replay
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=12:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail;umask 077;export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1
[[ "$#" -eq 6 ]]||exit 2;PAYLOAD_SHA="$1";RUN_TOKEN="$2";ARRAY_JOB="$3";REDUCER_JOB="$4";REDUCTION_SHA="$5";RECEIPT_NAME="$6"
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727;CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif;CONTAINER_SHA=aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4
cd "$ROOT";printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_payload.sha256|sha256sum -c - >/dev/null;sha256sum -c notes/isambard_ai_v4_r2_payload.sha256 >/dev/null;printf '%s  %s\n' "$CONTAINER_SHA" "$CONTAINER"|sha256sum -c - >/dev/null
[[ "$RECEIPT_NAME" =~ ^v4-r2-replay-[0-9]+\.json$ ]]||exit 2;OUT="$ROOT/artifacts/replay/$RECEIPT_NAME"
srun --ntasks=1 apptainer exec "$CONTAINER" python3 code/independent_replay_gpu_gating_v4_r2.py --run-token "$RUN_TOKEN" --array-job "$ARRAY_JOB" --reducer-job "$REDUCER_JOB" --reduction-sha256 "$REDUCTION_SHA" --output "$OUT"
