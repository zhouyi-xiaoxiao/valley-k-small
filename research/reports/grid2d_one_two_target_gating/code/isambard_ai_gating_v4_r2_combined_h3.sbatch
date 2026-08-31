#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-combined-h3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=08:00:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail; umask 077; export LC_ALL=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -eq 9 ]] || exit 2; PAYLOAD_SHA="$1"; V3_RELEASE="$2"; V3_SHA="$3"; REPLAY="$4"; REPLAY_SHA="$5"; REPLAY_JOB="$6"; REPLAY_SUBMIT="$7"; REPLAY_SUBMIT_SHA="$8"; COMBINED_SUBMIT="$9"
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727; CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
module load cray-python/3.11.7; HOST_PYTHON="$(command -v python3)"; HOST_VERSION="$("$HOST_PYTHON" -c 'import platform; print(platform.python_version())')"; [[ "$HOST_VERSION" == 3.11.7 && ":${LOADEDMODULES:-}:" == *":cray-python/3.11.7:"* ]] || exit 2
cd "$ROOT"; printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h3_payload.sha256 | sha256sum -c - >/dev/null; sha256sum -c notes/isambard_ai_v4_r2_h3_payload.sha256 >/dev/null; printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
RUNTIME="$ROOT/artifacts/runtime_h3/combined-${SLURM_JOB_ID:?}.json"; mkdir -p "$ROOT/artifacts/runtime_h3"; chmod 700 "$ROOT/artifacts/runtime_h3"; apptainer exec "$CONTAINER" python3 code/runtime_probe_v4_r2_h3.py --phase combined --job-id "$SLURM_JOB_ID" --host-python-executable "$HOST_PYTHON" --host-python-version "$HOST_VERSION" --loaded-modules "${LOADEDMODULES:-}" --container "$CONTAINER" --output "$RUNTIME"
OUT="$ROOT/artifacts/combined_h3/combined-$REPLAY_JOB-${SLURM_JOB_ID:?}"; mkdir -m 700 "$OUT"; apptainer exec "$CONTAINER" python3 code/analyze_gpu_gating_v4_r2_combined_h3.py --h3-payload-sha256 "$PAYLOAD_SHA" --v3-release "$V3_RELEASE" --v3-release-sha256 "$V3_SHA" --v4-replay-receipt "$REPLAY" --v4-replay-sha256 "$REPLAY_SHA" --replay-job "$REPLAY_JOB" --replay-submission "$REPLAY_SUBMIT" --replay-submission-sha256 "$REPLAY_SUBMIT_SHA" --combined-submission "$COMBINED_SUBMIT" --slurm-job-id "$SLURM_JOB_ID" --runtime-receipt "$RUNTIME" --output-json "$OUT/combined_v4_r2_h3.json" --output-csv "$OUT/combined_v4_r2_h3.csv"
