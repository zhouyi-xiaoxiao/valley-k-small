#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v3-reduce
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --no-requeue
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail
umask 077
export LC_ALL=C
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

MODE="${1:?missing reducer mode (inventory or full)}"
MANIFEST_RELATIVE="${2:?missing manifest path relative to the report root}"
FIELD_PACK_RELATIVE="${3:?missing field-pack path relative to the report root}"
PHASE="${4:?missing phase label}"
RUN_TOKEN="${5:?missing shared run token}"
ARRAY_JOB_ID="${6:?missing source array job id}"
EXPECTED_CELL_COUNT="${7:?missing expected array-cell count}"

REPORT_ROOT="${SLURM_SUBMIT_DIR:?missing SLURM_SUBMIT_DIR}"
SCRIPT_DIR="${REPORT_ROOT}/code"
CONTAINER="/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
OUTPUT_ROOT="${REPORT_ROOT}/artifacts/outputs/isambard_ai_v3"
RESULTS_DIR="${OUTPUT_ROOT}/${PHASE}-${RUN_TOKEN}"
REDUCTION_DIR="${OUTPUT_ROOT}/reductions/${PHASE}-${RUN_TOKEN}-reduce-${SLURM_JOB_ID}"
MANIFEST="${REPORT_ROOT}/${MANIFEST_RELATIVE}"
FIELD_PACK="${REPORT_ROOT}/${FIELD_PACK_RELATIVE}"
SACCT_RECEIPT="${REDUCTION_DIR}/sacct-${PHASE}-${RUN_TOKEN}.psv"
OUTPUT_CSV="${REDUCTION_DIR}/reduction.csv"
OUTPUT_JSON="${REDUCTION_DIR}/reduction.json"

case "${MANIFEST_RELATIVE}" in
  /*|*../*|../*|*/..) echo "manifest path escaped report root" >&2; exit 2 ;;
esac
case "${FIELD_PACK_RELATIVE}" in
  /*|*../*|../*|*/..) echo "field-pack path escaped report root" >&2; exit 2 ;;
esac
case "${RUN_TOKEN}" in
  ''|*[!0-9]*) echo "run token must contain decimal digits only" >&2; exit 2 ;;
esac
case "${EXPECTED_CELL_COUNT}" in
  ''|*[!0-9]*) echo "expected cell count must contain decimal digits only" >&2; exit 2 ;;
esac
case "${ARRAY_JOB_ID}" in
  ''|*[!0-9]*) echo "array job id must contain decimal digits only" >&2; exit 2 ;;
esac

if [[ "${MODE}:${PHASE}:${EXPECTED_CELL_COUNT}" == "inventory:canary:8" ]]; then
  EXPECTED_ALLOCATION_COUNT=8
elif [[ "${MODE}:${PHASE}:${EXPECTED_CELL_COUNT}" == "full:production:5760" ]]; then
  EXPECTED_ALLOCATION_COUNT=480
else
  echo "unsupported reducer contract: ${MODE}:${PHASE}:${EXPECTED_CELL_COUNT}" >&2
  exit 2
fi

cd "${REPORT_ROOT}"
sha256sum -c notes/isambard_ai_v3_payload.sha256 >/dev/null
[[ -f "${MANIFEST}" ]] || { echo "manifest does not exist: ${MANIFEST}" >&2; exit 2; }
[[ -f "${FIELD_PACK}" ]] || { echo "field pack does not exist: ${FIELD_PACK}" >&2; exit 2; }
[[ -d "${RESULTS_DIR}" ]] || { echo "results directory does not exist: ${RESULTS_DIR}" >&2; exit 2; }

mkdir -p "${OUTPUT_ROOT}/reductions"
mkdir -m 700 "${REDUCTION_DIR}"
SACCT_TEMP="$(mktemp "${REDUCTION_DIR}/.sacct-${PHASE}-${RUN_TOKEN}.XXXXXX")"
cleanup() {
  if [[ -n "${SACCT_TEMP}" ]]; then
    rm -f -- "${SACCT_TEMP}"
  fi
}
trap cleanup EXIT

receipt_ready=0
for attempt in $(seq 1 30); do
  sacct -X --array -j "${ARRAY_JOB_ID}" \
    --format=JobIDRaw,JobID,State,ExitCode --parsable2 > "${SACCT_TEMP}"
  observed_count="$({
    # On Isambard, JobIDRaw is an allocation-unique decimal number rather
    # than ARRAY_JOB_ID_TASK_ID.  Prefer the array-form JobID when exposed,
    # and otherwise count unique decimal allocation IDs while excluding the
    # parent array row.  The reducer subsequently validates every row against
    # the SLURM_JOB_ID/SLURM_ARRAY_JOB_ID captured in each result payload.
    awk -F '|' -v array_id="${ARRAY_JOB_ID}" -v prefix="${ARRAY_JOB_ID}_" '
      index($2, prefix) == 1 && $2 !~ /\./ {
        task = substr($2, length(prefix) + 1)
        if (task ~ /^[0-9]+$/) seen["task:" task] = 1
        next
      }
      $1 ~ /^[0-9]+$/ && $1 != array_id {
        seen["allocation:" $1] = 1
      }
      END {
        count = 0
        for (task in seen) count += 1
        print count
      }
    ' "${SACCT_TEMP}"
  } 2>/dev/null)"
  if [[ "${observed_count}" == "${EXPECTED_ALLOCATION_COUNT}" ]]; then
    receipt_ready=1
    break
  fi
  if [[ "${attempt}" -lt 30 ]]; then
    sleep 10
  fi
done
if [[ "${receipt_ready}" != 1 ]]; then
  echo "sacct did not expose all ${EXPECTED_ALLOCATION_COUNT} array allocations" >&2
  exit 3
fi
mv "${SACCT_TEMP}" "${SACCT_RECEIPT}"
SACCT_TEMP=""

srun --ntasks=1 apptainer exec "${CONTAINER}" \
  python3 "${SCRIPT_DIR}/reduce_gpu_gating_v3.py" \
  --mode "${MODE}" \
  --manifest "${MANIFEST}" \
  --field-pack "${FIELD_PACK}" \
  --results-dir "${RESULTS_DIR}" \
  --source "${SCRIPT_DIR}/gpu_gating_mc_v3.py" \
  --sacct-receipt "${SACCT_RECEIPT}" \
  --output-csv "${OUTPUT_CSV}" \
  --output-json "${OUTPUT_JSON}"

[[ -s "${OUTPUT_CSV}" ]] || { echo "reducer CSV commit is missing" >&2; exit 4; }
[[ -s "${OUTPUT_JSON}" ]] || { echo "reducer JSON commit is missing" >&2; exit 4; }
