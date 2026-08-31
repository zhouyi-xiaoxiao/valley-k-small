#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-canary-h1
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --gpus=4
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:10:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail; umask 077; export LC_ALL=C
[[ "$#" -eq 3 ]] || exit 2
PAYLOAD_SHA="$1"; RELEASE_SHA="$2"; RELEASE="$3"
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
cd "$ROOT"
printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h1_payload.sha256 | sha256sum -c - >/dev/null
sha256sum -c notes/isambard_ai_v4_r2_h1_payload.sha256 >/dev/null
printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
printf '%s  %s\n' "$RELEASE_SHA" "$RELEASE" | sha256sum -c - >/dev/null
python3 - "$RELEASE" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]));assert x["schema"]=="grid2d-one-two-target-gating-v3-release-for-v4-r2-h1";assert x["status"]=="PASS_AUTHORIZE_V4_R2_H1_HARDWARE_CANARY"
PY
OUT="$ROOT/artifacts/canary/canary-${SLURM_JOB_ID:?}"; mkdir -m 700 "$OUT"; pids=()
for lane in 0 1 2 3; do
  srun --exclusive --ntasks=1 --gpus-per-task=1 --gpu-bind=single:1 python3 code/capture_gpu_lane_v4_r2.py --lane "$lane" --output "$OUT/lane-$lane.json" & pids+=("$!")
done
status=0; set +e; for pid in "${pids[@]}"; do wait "$pid" || status=1; done; set -e
[[ "$status" -eq 0 ]] || exit 4
python3 code/verify_gpu_canary_v4_r2.py --lanes "$OUT" --release-receipt "$RELEASE" --release-sha256 "$RELEASE_SHA" --output "$OUT/canary-receipt.json"
