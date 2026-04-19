#!/usr/bin/env bash
set -e

ENV_NAME="agent-from-scratch"
PYTHON_VERSION="3.12"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create conda env if it doesn't exist
if ! conda env list | grep -q "^${ENV_NAME} "; then
    echo "Creating conda environment '${ENV_NAME}' with Python ${PYTHON_VERSION}..."
    conda create -y -n "$ENV_NAME" python="$PYTHON_VERSION"
fi

# Activate
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

echo "Python: $(python --version) ($(which python))"

# Install deps if needed
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
fi

# Forward all args to the CLI
cd "$SCRIPT_DIR/src"
exec python cli_event_driven.py "$@"
