#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v4-r2-release-h3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --no-requeue
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail; umask 077; export LC_ALL=C PYTHONHASHSEED=0
[[ "$#" -eq 9 ]] || exit 2; PAYLOAD_SHA="$1"; COMBINED_JOB="$2"; COMBINED_JSON="$3"; COMBINED_JSON_SHA="$4"; COMBINED_CSV="$5"; COMBINED_CSV_SHA="$6"; COMBINED_SUBMIT="$7"; COMBINED_SUBMIT_SHA="$8"; RELEASE_SUBMIT="$9"
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727; CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
module load cray-python/3.11.7; HOST_PYTHON="$(command -v python3)"; HOST_VERSION="$("$HOST_PYTHON" -c 'import platform; print(platform.python_version())')"; [[ "$HOST_VERSION" == 3.11.7 && ":${LOADEDMODULES:-}:" == *":cray-python/3.11.7:"* ]] || exit 2
cd "$ROOT"; printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h3_payload.sha256 | sha256sum -c - >/dev/null; sha256sum -c notes/isambard_ai_v4_r2_h3_payload.sha256 >/dev/null; printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | sha256sum -c - >/dev/null
RUNTIME="$ROOT/artifacts/runtime_h3/release-${SLURM_JOB_ID:?}.json"; mkdir -p "$ROOT/artifacts/runtime_h3" "$ROOT/artifacts/releases_h3"; chmod 700 "$ROOT/artifacts/runtime_h3" "$ROOT/artifacts/releases_h3"; apptainer exec "$CONTAINER" python3 code/runtime_probe_v4_r2_h3.py --phase release --job-id "$SLURM_JOB_ID" --host-python-executable "$HOST_PYTHON" --host-python-version "$HOST_VERSION" --loaded-modules "${LOADEDMODULES:-}" --container "$CONTAINER" --output "$RUNTIME"
TERMINAL="$ROOT/artifacts/releases_h3/combined-$COMBINED_JOB-terminal.psv"; sacct -X -j "$COMBINED_JOB" --format=JobIDRaw,JobID,State,ExitCode,ElapsedRaw,AllocTRES,ReqTRES,NNodes --parsable2 > "$TERMINAL"; chmod 600 "$TERMINAL"; OUT="$ROOT/artifacts/releases_h3/final-release-$COMBINED_JOB.json"
apptainer exec "$CONTAINER" python3 code/finalize_gpu_gating_v4_r2_h3.py --h3-payload-sha256 "$PAYLOAD_SHA" --combined-job "$COMBINED_JOB" --combined-json "$COMBINED_JSON" --combined-json-sha256 "$COMBINED_JSON_SHA" --combined-csv "$COMBINED_CSV" --combined-csv-sha256 "$COMBINED_CSV_SHA" --combined-submission "$COMBINED_SUBMIT" --combined-submission-sha256 "$COMBINED_SUBMIT_SHA" --release-submission "$RELEASE_SUBMIT" --release-job "$SLURM_JOB_ID" --terminal-receipt "$TERMINAL" --runtime-receipt "$RUNTIME" --output "$OUT"
