#!/bin/bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v3-authority-h13
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=128G
#SBATCH --time=18:00:00
#SBATCH --no-requeue
#SBATCH --export=NIL
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727/logs/%x-%j.err
set -euo pipefail
umask 077
unset BASH_ENV ENV CDPATH GLOBIGNORE PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONINSPECT PYTHONBREAKPOINT LD_PRELOAD LD_LIBRARY_PATH
export PATH=/usr/bin:/bin LC_ALL=C LANG=C PYTHONHASHSEED=0 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
[[ "$#" -ge 10 ]] || exit 2
PAYLOAD_SHA="$1"
INPUT_SCHEMA="$2"
RELEASE_SCHEMA="$3"
RELEASE_STATUS="$4"
AUDIT_SCHEMA="$5"
AUDIT_STATUS="$6"
SECONDARY_JOB="$7"
PUBLICATION_NAME="$8"
ACCOUNTING_PATH="$9"
ACCOUNTING_SHA="${10}"
shift 10
[[ "$INPUT_SCHEMA" == h13-secondary-authority-cli-v1 ]] || exit 2
[[ "$RELEASE_SCHEMA" != *PENDING* && "$RELEASE_STATUS" != *PENDING* && "$AUDIT_SCHEMA" != *PENDING* && "$AUDIT_STATUS" != *PENDING* ]] || exit 2
[[ "$SECONDARY_JOB" =~ ^[1-9][0-9]*$ && "$PUBLICATION_NAME" == *-"$SECONDARY_JOB" ]] || exit 2
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
CONTAINER=/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif
cd "$ROOT"
/usr/bin/printf '%s  %s\n' "$PAYLOAD_SHA" notes/isambard_ai_v4_r2_h13_payload.sha256 | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/sha256sum -c notes/isambard_ai_v4_r2_h13_payload.sha256 >/dev/null
/usr/bin/printf '%s  %s\n' aac14468290a4b1489806a47e26ada96b741afbbe2edfe8fa2bf5424013f09c4 "$CONTAINER" | /usr/bin/sha256sum -c - >/dev/null
/usr/bin/printf '%s  %s\n' "$ACCOUNTING_SHA" "$ACCOUNTING_PATH" | /usr/bin/sha256sum -c - >/dev/null
h13_pinned_source | /usr/bin/apptainer exec "$CONTAINER" python3 -I -B -E -s - \
  "$PAYLOAD_SHA" code/verify_v3_release_for_v4_r2_h13.py \
  --h13-payload-sha256 "$PAYLOAD_SHA" \
  --input-contract-schema "$INPUT_SCHEMA" \
  --secondary-release-schema "$RELEASE_SCHEMA" \
  --secondary-release-status "$RELEASE_STATUS" \
  --secondary-audit-schema "$AUDIT_SCHEMA" \
  --secondary-audit-status "$AUDIT_STATUS" \
  --secondary-job-id "$SECONDARY_JOB" \
  --publication-name "$PUBLICATION_NAME" \
  --secondary-accounting "$ACCOUNTING_PATH" \
  --secondary-accounting-sha256 "$ACCOUNTING_SHA" \
  "$@" \
  --output "$ROOT/artifacts/releases/v3-release-for-v4-r2-h13.json"
