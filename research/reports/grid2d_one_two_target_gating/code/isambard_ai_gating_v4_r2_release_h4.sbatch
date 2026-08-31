#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-release-h4
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
[[ "$#" -eq 12 ]] || exit 2
PAYLOAD_SHA="$1"; ARRAY_JOB="$2"; REDUCER_JOB="$3"; REPLAY_JOB="$4"; COMBINED_JOB="$5"; V3_SHA="$6"; REPLAY_SHA="$7"; REPLAY_SUBMIT_SHA="$8"; COMBINED_SUBMIT_SHA="$9"; COMBINED_JSON_SHA="${10}"; COMBINED_CSV_SHA="${11}"; RELEASE_SUBMIT="${12}"
[[ "$ARRAY_JOB" =~ ^[0-9]+$ && "$REDUCER_JOB" =~ ^[0-9]+$ && "$REPLAY_JOB" =~ ^[0-9]+$ && "$COMBINED_JOB" =~ ^[0-9]+$ ]] || exit 2
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
CANONICAL="$ROOT/artifacts/combined_h4/replay-$REPLAY_JOB-combined-$COMBINED_JOB"
COMBINED_JSON="$CANONICAL/combined_v4_r2_h4.json"
COMBINED_CSV="$CANONICAL/combined_v4_r2_h4.csv"
[[ "$RELEASE_SUBMIT" == "$ROOT/artifacts/submission_h4/release-submission.json" ]] || exit 2
module load cray-python/3.11.7
HOST_PYTHON="$(command -v python3)"
HOST_VERSION="$("$HOST_PYTHON" -c 'import platform; print(platform.python_version())')"
[[ "$HOST_VERSION" == 3.11.7 && ":${LOADEDMODULES:-}:" == *":cray-python/3.11.7:"* ]] || exit 2
cd "$ROOT"
printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h4_payload.sha256 | sha256sum -c - >/dev/null
sha256sum -c notes/isambard_ai_v4_r2_h4_payload.sha256 >/dev/null
printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
for _attempt in $(seq 1 120); do [[ -s "$RELEASE_SUBMIT" ]] && break; sleep 1; done
[[ -f "$RELEASE_SUBMIT" && ! -L "$RELEASE_SUBMIT" ]] || exit 2
printf '%s  %s\n' "$COMBINED_JSON_SHA" "$COMBINED_JSON" | sha256sum -c - >/dev/null
printf '%s  %s\n' "$COMBINED_CSV_SHA" "$COMBINED_CSV" | sha256sum -c - >/dev/null
RUNTIME="$ROOT/artifacts/runtime_h4/release-${SLURM_JOB_ID:?}.json"
RELEASE_DIR="$ROOT/artifacts/releases_h4"
mkdir -p "$ROOT/artifacts/runtime_h4" "$RELEASE_DIR"
chmod 700 "$ROOT/artifacts/runtime_h4" "$RELEASE_DIR"
apptainer exec "$CONTAINER" python3 code/runtime_probe_v4_r2_h4.py --phase release --job-id "$SLURM_JOB_ID" --host-python-executable "$HOST_PYTHON" --host-python-version "$HOST_VERSION" --loaded-modules "${LOADEDMODULES:-}" --container "$CONTAINER" --output "$RUNTIME"
TERMINAL="$RELEASE_DIR/replay-$REPLAY_JOB-combined-$COMBINED_JOB-terminal.psv"
sacct -X -j "$COMBINED_JOB" --format=JobIDRaw,JobID,State,ExitCode,ElapsedRaw,AllocTRES,ReqTRES,NNodes --parsable2 > "$TERMINAL"
chmod 600 "$TERMINAL"
apptainer exec "$CONTAINER" python3 code/finalize_gpu_gating_v4_r2_h4.py --h4-payload-sha256 "$PAYLOAD_SHA" --array-job "$ARRAY_JOB" --reducer-job "$REDUCER_JOB" --replay-job "$REPLAY_JOB" --combined-job "$COMBINED_JOB" --release-job "$SLURM_JOB_ID" --v3-release-sha256 "$V3_SHA" --v4-replay-sha256 "$REPLAY_SHA" --replay-submission-sha256 "$REPLAY_SUBMIT_SHA" --combined-submission-sha256 "$COMBINED_SUBMIT_SHA" --combined-json-sha256 "$COMBINED_JSON_SHA" --combined-csv-sha256 "$COMBINED_CSV_SHA"
