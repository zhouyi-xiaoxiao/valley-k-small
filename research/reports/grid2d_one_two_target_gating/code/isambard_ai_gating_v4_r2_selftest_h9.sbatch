#!/usr/bin/env bash
#SBATCH --job-name=vk-h9-selftest
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:01:00
#SBATCH --chdir=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
set -euo pipefail
ROOT=/home/b5dj/ae23069.b5dj/valley-gating-v4-fullnode-r2-20260727
cd "$ROOT"
[[ "$#" -eq 2 ]]
mkdir -p artifacts/h9_e2e
printf '%s\n' "$1:$2" > "artifacts/h9_e2e/${H9_TEST_OUTPUT_NAME:?}.txt"

