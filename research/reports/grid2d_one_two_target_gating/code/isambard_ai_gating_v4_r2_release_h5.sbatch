#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-release-h5
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
[[ "$#" -eq 13 ]] || exit 2
H5_SHA="$1"; H4_SHA="$2"; ARRAY_JOB="$3"; REDUCER_JOB="$4"; REPLAY_JOB="$5"; COMBINED_JOB="$6"; V3_SHA="$7"; REPLAY_SHA="$8"; REPLAY_SUBMIT_SHA="$9"; COMBINED_SUBMIT_SHA="${10}"; COMBINED_JSON_SHA="${11}"; COMBINED_CSV_SHA="${12}"; RELEASE_SUBMIT="${13}"
[[ "$ARRAY_JOB" =~ ^[0-9]+$ && "$REDUCER_JOB" =~ ^[0-9]+$ && "$REPLAY_JOB" =~ ^[0-9]+$ && "$COMBINED_JOB" =~ ^[0-9]+$ ]] || exit 2
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
[[ "$RELEASE_SUBMIT" == "$ROOT/artifacts/submission_h5/release-submission.json" ]] || exit 2
module load cray-python/3.11.7
HOST_PYTHON="$(command -v python3)"
HOST_VERSION="$("$HOST_PYTHON" -c 'import platform; print(platform.python_version())')"
[[ "$HOST_VERSION" == 3.11.7 && ":${LOADEDMODULES:-}:" == *":cray-python/3.11.7:"* ]] || exit 2
cd "$ROOT"
printf '%s  %s\n' "$H5_SHA" notes/isambard_ai_v4_r2_h5_payload.sha256 | sha256sum -c - >/dev/null
sha256sum -c notes/isambard_ai_v4_r2_h5_payload.sha256 >/dev/null
printf '%s  %s\n' "$H4_SHA" notes/isambard_ai_v4_r2_h4_payload.sha256 | sha256sum -c - >/dev/null
printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
for _attempt in $(seq 1 120); do [[ -s "$RELEASE_SUBMIT" ]] && break; sleep 1; done
[[ -f "$RELEASE_SUBMIT" && ! -L "$RELEASE_SUBMIT" ]] || exit 2
RUNTIME="$ROOT/artifacts/runtime_h5/release-${SLURM_JOB_ID:?}.json"
mkdir -p "$ROOT/artifacts/runtime_h5"; chmod 700 "$ROOT/artifacts/runtime_h5"
apptainer exec "$CONTAINER" python3 code/runtime_probe_v4_r2_h5.py --phase release --job-id "$SLURM_JOB_ID" --host-python-executable "$HOST_PYTHON" --host-python-version "$HOST_VERSION" --loaded-modules "${LOADEDMODULES:-}" --container "$CONTAINER" --output "$RUNTIME"
INPUT_DIR="$ROOT/artifacts/releases_h5/provisional_inputs/array-$ARRAY_JOB-reducer-$REDUCER_JOB-replay-$REPLAY_JOB-combined-$COMBINED_JOB-release-${SLURM_JOB_ID}"
mkdir -p "$INPUT_DIR"; chmod 700 "$INPUT_DIR"
TERMINAL="$INPUT_DIR/combined-terminal.psv"
[[ ! -e "$TERMINAL" ]] || exit 2
TEMP_TERMINAL="$(mktemp "$INPUT_DIR/.combined-terminal.XXXXXX")"
trap 'rm -f "$TEMP_TERMINAL"' EXIT
sacct -X -j "$COMBINED_JOB" --format=JobIDRaw,JobID,State,ExitCode,ElapsedRaw,AllocTRES,ReqTRES,NNodes --parsable2 > "$TEMP_TERMINAL"
chmod 600 "$TEMP_TERMINAL"
ln "$TEMP_TERMINAL" "$TERMINAL"
rm -f "$TEMP_TERMINAL"
trap - EXIT
apptainer exec "$CONTAINER" python3 code/provision_gpu_gating_v4_r2_h5.py --h5-payload-sha256 "$H5_SHA" --h4-payload-sha256 "$H4_SHA" --array-job "$ARRAY_JOB" --reducer-job "$REDUCER_JOB" --replay-job "$REPLAY_JOB" --combined-job "$COMBINED_JOB" --release-job "$SLURM_JOB_ID" --v3-release-sha256 "$V3_SHA" --v4-replay-sha256 "$REPLAY_SHA" --replay-submission-sha256 "$REPLAY_SUBMIT_SHA" --combined-submission-sha256 "$COMBINED_SUBMIT_SHA" --combined-json-sha256 "$COMBINED_JSON_SHA" --combined-csv-sha256 "$COMBINED_CSV_SHA"
