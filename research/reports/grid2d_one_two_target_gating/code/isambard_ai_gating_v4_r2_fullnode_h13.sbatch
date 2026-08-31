#!/bin/bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-fullnode-h13
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --gpus=4
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=02:00:00
#SBATCH --array=0-479%240
#SBATCH --no-requeue
#SBATCH --export=NIL
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%A_%a.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%A_%a.err
set -euo pipefail
umask 077
unset BASH_ENV ENV CDPATH GLOBIGNORE PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONBREAKPOINT LD_PRELOAD LD_LIBRARY_PATH
export PATH=/usr/bin:/bin LC_ALL=C LANG=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -eq 5 ]] || exit 2
PAYLOAD_SHA="$1"; RELEASE="$2"; RELEASE_SHA="$3"; CANARY="$4"; CANARY_SHA="$5"
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
MANIFEST="$ROOT/artifacts/data/gating_v4_r2_production_manifest.json"
PACK="$ROOT/artifacts/data/disorder_field_pack_v4_r2_reflect.npz"
TASK="${SLURM_ARRAY_TASK_ID:?}"; RUN_TOKEN="${SLURM_ARRAY_JOB_ID:?}"
RESULTS="$ROOT/artifacts/outputs/isambard_ai_v4_r2/production-$RUN_TOKEN"
[[ "$TASK" =~ ^[0-9]+$ && "$TASK" -le 479 && "$RUN_TOKEN" =~ ^[0-9]+$ ]] || exit 2
cd "$ROOT"
/usr/bin/printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h13_payload.sha256 | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/sha256sum -c notes/isambard_ai_v4_r2_h13_payload.sha256 >/dev/null
/usr/bin/printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/printf '%s  %s\n' "$RELEASE_SHA" "$RELEASE" | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/printf '%s  %s\n' "$CANARY_SHA" "$CANARY" | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/apptainer exec "$CONTAINER" python3 -I -B -E -s - "$RELEASE" "$CANARY" "$RELEASE_SHA" <<'PY'
import json,sys
r=json.load(open(sys.argv[1])); c=json.load(open(sys.argv[2])); assert r["schema"]=="grid2d-one-two-target-gating-v3-release-for-v4-r2-h13" and r["status"]=="PASS_AUTHORIZE_V4_R2_H13_HARDWARE_CANARY" and r["authorizes_v4_r2_h13"] is True and r["authority_boundary"]["authorizes_reducer_or_later"] is False; assert c["schema"]=="grid2d-one-two-target-gating-v4-r2-gpu-canary-h13-v1" and c["status"]=="PASS_AUTHORIZE_V4_R2_PRODUCTION" and c["release_receipt_sha256"]==sys.argv[3] and c["distinct_uuid_count"]==c["distinct_pci_count"]==c["distinct_cuda_visible_devices_count"]==4
PY
h13_pinned_source | /usr/bin/apptainer exec "$CONTAINER" python3 -I -B -E -s - "$PAYLOAD_SHA" code/validate_gating_campaign_manifest_v4_r2.py --manifest "$MANIFEST" >/dev/null
/usr/bin/mkdir -p "$RESULTS"; /bin/chmod 700 "$RESULTS"
run_lane(){
  local gpu="$1" bundle cell dir tmp
  tmp="/tmp/v4r2h4-$RUN_TOKEN-${SLURM_JOB_ID}-${TASK}-$gpu"
  /usr/bin/mkdir -m 700 "$tmp"
  for bundle in $(/usr/bin/seq 0 11); do
    cell=$((10#$TASK+480*(10#$gpu+4*bundle)))
    dir="$RESULTS/cell-$cell"; /usr/bin/mkdir -m 700 "$dir"
    h13_pinned_source | TMPDIR="$tmp" /usr/bin/srun --exclusive --ntasks=1 --gpus-per-task=1 --cpus-per-task=8 --gpu-bind=single:1 /usr/bin/apptainer exec --nv "$CONTAINER" python3 -I -B -E -s - "$PAYLOAD_SHA" code/gpu_gating_mc_v4_r2.py --manifest "$MANIFEST" --field-pack "$PACK" --cell-id "$cell" --device cuda --output-json "$dir/cell-$cell.json" --output-npz "$dir/cell-$cell.npz" || return $?
  done
}
pids=()
for gpu in 0 1 2 3; do run_lane "$gpu" & pids+=("$!"); done
status=0
set +e
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
set -e
[[ "$status" -eq 0 ]] || exit 4
for gpu in 0 1 2 3; do
  for bundle in $(/usr/bin/seq 0 11); do
    cell=$((10#$TASK+480*(gpu+4*bundle))); dir="$RESULTS/cell-$cell"
    [[ $(/usr/bin/find "$dir" -mindepth 1 -maxdepth 1 -type f ! -name '.*' | /usr/bin/wc -l) -eq 2 && -s "$dir/cell-$cell.json" && -s "$dir/cell-$cell.npz" ]] || exit 5
  done
done
