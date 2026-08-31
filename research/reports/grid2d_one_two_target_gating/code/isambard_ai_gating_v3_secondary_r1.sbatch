#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v3-secondary-r1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --no-requeue
#SBATCH --dependency=afterok:5788358
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727
#SBATCH --output=/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727/logs/%x-%j.out
#SBATCH --error=/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727/logs/%x-%j.err

# Submit with the frozen digest of notes/isambard_ai_v3_secondary_r1.sha256:
#   sbatch code/isambard_ai_gating_v3_secondary_r1.sbatch <manifest_sha256>
# The digest becomes immutable Slurm argv while queued.  This resolves the
# intentional cycle in which the payload manifest also hashes this sbatch.

set -euo pipefail
umask 077
export LC_ALL=C
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

[[ "$#" -eq 1 ]] || { echo "expected exactly the frozen payload-manifest SHA-256" >&2; exit 2; }
EXPECTED_PAYLOAD_MANIFEST_SHA256="$1"
[[ "${EXPECTED_PAYLOAD_MANIFEST_SHA256}" =~ ^[0-9a-f]{64}$ ]] || {
  echo "payload-manifest SHA-256 must be 64 lowercase hexadecimal digits" >&2
  exit 2
}

UPSTREAM_ROOT="/home/b5dj/ae23069.b5dj/valley-gating-v3-20260726-r3"
SECONDARY_ROOT="/home/b5dj/ae23069.b5dj/valley-gating-v3-secondary-r1-20260727"
REDUCTION_DIR="${UPSTREAM_ROOT}/artifacts/outputs/isambard_ai_v3/reductions/production-5788353-reduce-5788358"
RAW_RESULTS_ROOT="${UPSTREAM_ROOT}/artifacts/outputs/isambard_ai_v3/production-5788353"
CONTRACT="${SECONDARY_ROOT}/notes/isambard_ai_v3_secondary_analysis_contract_r1.json"
PAYLOAD_MANIFEST="${SECONDARY_ROOT}/notes/isambard_ai_v3_secondary_r1.sha256"
MANIFEST="${UPSTREAM_ROOT}/artifacts/data/gating_v3_production_manifest.json"
REDUCTION_JSON="${REDUCTION_DIR}/reduction.json"
REDUCTION_CSV="${REDUCTION_DIR}/reduction.csv"
SACCT_RECEIPT="${REDUCTION_DIR}/sacct-production-5788353.psv"
ANALYZER="${SECONDARY_ROOT}/code/analyze_gpu_gating_v3_secondary_r1.py"
CONTAINER="/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
OUTPUT_PARENT="${SECONDARY_ROOT}/artifacts/outputs/isambard_ai_v3/secondary_r1"
OUTPUT_DIR="${OUTPUT_PARENT}/upstream-5788358-secondary-${SLURM_JOB_ID:?missing SLURM_JOB_ID}"

[[ "${SLURM_SUBMIT_DIR:?missing SLURM_SUBMIT_DIR}" == "${SECONDARY_ROOT}" ]] || {
  echo "submission directory is not the independent secondary root" >&2
  exit 2
}
[[ -d "${UPSTREAM_ROOT}" && ! -L "${UPSTREAM_ROOT}" ]] || { echo "upstream root missing or symlinked" >&2; exit 3; }
[[ -d "${SECONDARY_ROOT}" && ! -L "${SECONDARY_ROOT}" ]] || { echo "secondary root missing or symlinked" >&2; exit 3; }
[[ -d "${RAW_RESULTS_ROOT}" && ! -L "${RAW_RESULTS_ROOT}" ]] || { echo "raw production root missing or symlinked" >&2; exit 3; }

cd "${SECONDARY_ROOT}"
printf '%s  %s\n' "${EXPECTED_PAYLOAD_MANIFEST_SHA256}" "notes/isambard_ai_v3_secondary_r1.sha256" | sha256sum -c - >/dev/null
sha256sum -c "${PAYLOAD_MANIFEST}" >/dev/null

for input in "${CONTRACT}" "${PAYLOAD_MANIFEST}" "${MANIFEST}" "${REDUCTION_JSON}" "${REDUCTION_CSV}" "${SACCT_RECEIPT}" "${ANALYZER}" "${CONTAINER}"; do
  [[ -f "${input}" && ! -L "${input}" ]] || { echo "missing or symlinked input: ${input}" >&2; exit 3; }
done

# This is the first and only write section.  Every target is rooted beneath
# SECONDARY_ROOT; UPSTREAM_ROOT remains read-only for the entire script.
mkdir -p "${OUTPUT_PARENT}"
mkdir -m 700 "${OUTPUT_DIR}"

srun --ntasks=1 apptainer exec "${CONTAINER}" \
  python3 "${ANALYZER}" \
  --contract "${CONTRACT}" \
  --payload-manifest "${PAYLOAD_MANIFEST}" \
  --expected-payload-manifest-sha256 "${EXPECTED_PAYLOAD_MANIFEST_SHA256}" \
  --manifest "${MANIFEST}" \
  --reduction-json "${REDUCTION_JSON}" \
  --reduction-csv "${REDUCTION_CSV}" \
  --sacct-receipt "${SACCT_RECEIPT}" \
  --output-json "${OUTPUT_DIR}/secondary_max_t_r1.json" \
  --output-csv "${OUTPUT_DIR}/secondary_max_t_r1.csv"

[[ -s "${OUTPUT_DIR}/secondary_max_t_r1.json" ]] || { echo "secondary JSON missing" >&2; exit 4; }
[[ -s "${OUTPUT_DIR}/secondary_max_t_r1.csv" ]] || { echo "secondary CSV missing" >&2; exit 4; }
MEMBERS="$(find "${OUTPUT_DIR}" -mindepth 1 -maxdepth 1 -type f -printf '%f\n' | LC_ALL=C sort)"
EXPECTED="$(printf '%s\n' secondary_max_t_r1.csv secondary_max_t_r1.json | LC_ALL=C sort)"
[[ "${MEMBERS}" == "${EXPECTED}" ]] || { echo "unexpected secondary output member" >&2; exit 4; }
chmod 600 "${OUTPUT_DIR}/secondary_max_t_r1.json" "${OUTPUT_DIR}/secondary_max_t_r1.csv"
