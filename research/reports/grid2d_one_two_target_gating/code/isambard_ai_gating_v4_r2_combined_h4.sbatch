#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-combined-h4
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=08:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail
umask 077
export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -eq 7 ]] || exit 2
PAYLOAD_SHA="$1"; ARRAY_JOB="$2"; REDUCER_JOB="$3"; REPLAY_JOB="$4"; V3_SHA="$5"; REPLAY_SHA="$6"; REPLAY_SUBMIT_SHA="$7"
[[ "$ARRAY_JOB" =~ ^[0-9]+$ && "$REDUCER_JOB" =~ ^[0-9]+$ && "$REPLAY_JOB" =~ ^[0-9]+$ ]] || exit 2
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
COMBINED_SUBMIT="$ROOT/artifacts/submission_h4/combined-submission.json"
module load cray-python/3.11.7
HOST_PYTHON="$(command -v python3)"
HOST_VERSION="$("$HOST_PYTHON" -c 'import platform; print(platform.python_version())')"
[[ "$HOST_VERSION" == 3.11.7 && ":${LOADEDMODULES:-}:" == *":cray-python/3.11.7:"* ]] || exit 2
cd "$ROOT"
printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h4_payload.sha256 | sha256sum -c - >/dev/null
sha256sum -c notes/isambard_ai_v4_r2_h4_payload.sha256 >/dev/null
printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
for _attempt in $(seq 1 120); do [[ -s "$COMBINED_SUBMIT" ]] && break; sleep 1; done
[[ -f "$COMBINED_SUBMIT" && ! -L "$COMBINED_SUBMIT" ]] || exit 2
COMBINED_SUBMIT_SHA="$(sha256sum "$COMBINED_SUBMIT" | awk '{print $1}')"
RUNTIME="$ROOT/artifacts/runtime_h4/combined-${SLURM_JOB_ID:?}.json"
mkdir -p "$ROOT/artifacts/runtime_h4"; chmod 700 "$ROOT/artifacts/runtime_h4"
apptainer exec "$CONTAINER" python3 code/runtime_probe_v4_r2_h4.py --phase combined --job-id "$SLURM_JOB_ID" --host-python-executable "$HOST_PYTHON" --host-python-version "$HOST_VERSION" --loaded-modules "${LOADEDMODULES:-}" --container "$CONTAINER" --output "$RUNTIME"
apptainer exec "$CONTAINER" python3 code/analyze_gpu_gating_v4_r2_combined_h4.py --h4-payload-sha256 "$PAYLOAD_SHA" --array-job "$ARRAY_JOB" --reducer-job "$REDUCER_JOB" --replay-job "$REPLAY_JOB" --slurm-job-id "$SLURM_JOB_ID" --v3-release-sha256 "$V3_SHA" --v4-replay-sha256 "$REPLAY_SHA" --replay-submission-sha256 "$REPLAY_SUBMIT_SHA" --combined-submission-sha256 "$COMBINED_SUBMIT_SHA"
