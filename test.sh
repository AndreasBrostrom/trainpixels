#!/bin/bash

# Remove virtual environment first
if [[ "$1" == "-r" ]]; then
    [[ -d venv ]] && rm -r venv
    [[ -d src/__pycache__ ]] && rm -r src/__pycache__
    shift  # Remove -r from arguments
fi

# Start
if [[ ! -d venv ]]; then
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo
else
    source venv/bin/activate
fi

python3 src/test.py "$@"
