#!/bin/bash

# Remove virtual environment first
if [[ "$1" == "-r" ]]; then
    rm -r venv
    rm -r src/__pycache__
    shift  # Remove -r from arguments

fi

# Start
if [[ ! -d venv ]]; then
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python3 src/main.py "$@"
