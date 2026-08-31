#!/usr/bin/env bash
#SBATCH --account=brics.b35cz
#SBATCH --partition=grace
#SBATCH --job-name=vk-gating-v3-i3-oracle
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
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

REPORT_ROOT="${SLURM_SUBMIT_DIR:?missing SLURM_SUBMIT_DIR}"
SCRIPT_DIR="${REPORT_ROOT}/code"
MANIFEST="${REPORT_ROOT}/artifacts/data/gating_v3_production_manifest.json"
OUTPUT_ROOT="${REPORT_ROOT}/artifacts/outputs/isambard3_exact_oracle_v3"
RESULT_DIR="${OUTPUT_ROOT}/oracle-${SLURM_JOB_ID}"
OUTPUT_JSON="${RESULT_DIR}/exact_homogeneous_oracle_v3.json"
TIME_LEDGER="${RESULT_DIR}/gnu-time.txt"

module load cray-python/3.12.12
cd "${REPORT_ROOT}"
sha256sum -c notes/isambard_ai_v3_payload.sha256 >/dev/null
[[ -f "${MANIFEST}" ]] || { echo "production manifest does not exist: ${MANIFEST}" >&2; exit 2; }

mkdir -p "${OUTPUT_ROOT}"
mkdir -m 700 "${RESULT_DIR}"
[[ ! -e "${OUTPUT_JSON}" ]] || { echo "refusing to overwrite oracle output" >&2; exit 2; }
[[ ! -e "${TIME_LEDGER}" ]] || { echo "refusing to overwrite time ledger" >&2; exit 2; }

srun --ntasks=1 /usr/bin/time -v -o "${TIME_LEDGER}" \
  python3 "${SCRIPT_DIR}/exact_homogeneous_oracle_v3.py" \
  --manifest "${MANIFEST}" \
  --output-json "${OUTPUT_JSON}"

[[ -s "${OUTPUT_JSON}" ]] || { echo "oracle output commit is missing" >&2; exit 3; }
[[ -s "${TIME_LEDGER}" ]] || { echo "GNU time ledger is missing" >&2; exit 3; }
