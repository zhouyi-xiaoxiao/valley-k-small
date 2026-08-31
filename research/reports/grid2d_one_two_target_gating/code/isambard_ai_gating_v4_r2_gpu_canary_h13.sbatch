#!/bin/bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-canary-h13
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --gpus=4
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:10:00
#SBATCH --no-requeue
#SBATCH --export=NIL
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail
umask 077
unset BASH_ENV ENV CDPATH GLOBIGNORE PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONBREAKPOINT LD_PRELOAD LD_LIBRARY_PATH
export PATH=/usr/bin:/bin LC_ALL=C LANG=C PYTHONHASHSEED=0
[[ "$#" -eq 3 ]] || exit 2
PAYLOAD_SHA="$1"; RELEASE_SHA="$2"; RELEASE="$3"
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
cd "$ROOT"
/usr/bin/printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h13_payload.sha256 | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/sha256sum -c notes/isambard_ai_v4_r2_h13_payload.sha256 >/dev/null
/usr/bin/printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/printf '%s  %s\n' "$RELEASE_SHA" "$RELEASE" | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/apptainer exec "$CONTAINER" python3 -I -B -E -s - "$RELEASE" <<'PY'
import json,sys
x=json.load(open(sys.argv[1])); assert x["schema"]=="grid2d-one-two-target-gating-v3-release-for-v4-r2-h13" and x["status"]=="PASS_AUTHORIZE_V4_R2_H13_HARDWARE_CANARY" and x["authorizes_v4_r2_h13"] is True and x["authority_boundary"]["authorizes_only_h13_canary_then_production"] is True and x["authority_boundary"]["authorizes_reducer_or_later"] is False
PY
OUT="$ROOT/artifacts/canary/canary-${SLURM_JOB_ID:?}"
/usr/bin/mkdir -m 700 "$OUT"
pids=()
for lane in 0 1 2 3; do
  h13_pinned_source | /usr/bin/srun --exclusive --ntasks=1 --gpus-per-task=1 --gpu-bind=single:1 /usr/bin/apptainer exec --nv "$CONTAINER" python3 -I -B -E -s - "$PAYLOAD_SHA" code/capture_gpu_lane_v4_r2.py --lane "$lane" --output "$OUT/lane-$lane.json" &
  pids+=("$!")
done
status=0
set +e
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
set -e
[[ "$status" -eq 0 ]] || exit 4
h13_pinned_source | /usr/bin/apptainer exec --nv "$CONTAINER" python3 -I -B -E -s - "$PAYLOAD_SHA" code/verify_gpu_canary_v4_r2_h13.py --lanes "$OUT" --release-receipt "$RELEASE" --release-sha256 "$RELEASE_SHA" --output "$OUT/canary-receipt.json"
