#!/usr/bin/env bash
#SBATCH --account=brics.b5dj
#SBATCH --partition=workq
#SBATCH --job-name=vk-gating-v3-env
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-gpu=8
#SBATCH --mem=32G
#SBATCH --time=00:10:00
#SBATCH --no-requeue
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail
umask 077
export LC_ALL=C

REPORT_ROOT="${SLURM_SUBMIT_DIR:?missing SLURM_SUBMIT_DIR}"
SCRIPT_DIR="${REPORT_ROOT}/code"
CONTAINER="/projects/public/brics/containers/e4s/e4s-cuda90-aarch64-25.11.sif"
RESULT_DIR="${REPORT_ROOT}/artifacts/outputs/isambard_ai_v3/environment-${SLURM_JOB_ID}"

cd "${REPORT_ROOT}"
sha256sum -c notes/isambard_ai_v3_payload.sha256
sha256sum -c notes/isambard_ai_v3_container.sha256
mkdir -p "${RESULT_DIR}"
srun --ntasks=1 apptainer exec --nv "${CONTAINER}" \
  python3 -c 'import json, numpy, platform, scipy, torch; assert torch.cuda.is_available(); print(json.dumps({"python": platform.python_version(), "numpy": numpy.__version__, "scipy": scipy.__version__, "torch": torch.__version__, "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)}, sort_keys=True))' \
  > "${RESULT_DIR}/runtime.json"
nvidia-smi -L > "${RESULT_DIR}/nvidia-smi-L.txt"
