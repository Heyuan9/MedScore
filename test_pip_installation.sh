#!/bin/bash
#
# This script automates the process of testing the MedScore package installation.
# It performs the following steps:
# 1. Defines the environment name and the package URL.
# 2. Creates a new, isolated conda environment with Python 3.9.
# 3. Installs the MedScore package from the specified GitHub branch using pip.
# 4. Runs the package's help command to verify the installation.
# 5. Removes the temporary conda environment to clean up.
#
# The script will exit immediately if any command fails.

# --- Configuration ---
# Use a specific name for the temporary environment to avoid conflicts.
ENV_NAME="medscore_temp_env"
BRANCH="presenticized"
# The correct git URL format for pip to install from a specific branch.
GIT_URL="git+https://github.com/Heyuan9/MedScore.git@${BRANCH}"

# --- Cleanup function ---
cleanup() {
    echo
    echo ">>> Cleaning up: Removing the temporary environment '${ENV_NAME}'..."
    conda env remove -n ${ENV_NAME} -y || true
}
trap cleanup EXIT

# --- Script Execution ---
# Exit immediately if a command exits with a non-zero status.
set -e

echo ">>> Step 1: Creating a temporary conda environment named '${ENV_NAME}'..."
conda create -n "${ENV_NAME}" python=3.12 -y

echo
echo ">>> Step 2: Installing MedScore..."
# Use 'conda run' to execute commands within the new environment
# without needing to activate it in the script's shell.
conda run -n "${ENV_NAME}" pip install "${GIT_URL}"

echo
echo ">>> Step 3: Verifying installation by running the --help command..."
conda run -n "${ENV_NAME}" python -m medscore.medscore --help

conda run -n "${ENV_NAME}" python -m medscore.medscore --config "demo/config.yaml"

echo
echo "✅ Script completed successfully!"
