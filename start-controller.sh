#!/bin/bash

# Remove virtual environment first
if [[ "$1" == "-r" ]]; then
    [[ -d venv ]] && rm -r venv
    [[ -d src/__pycache__ ]] && rm -r src/__pycache__
    shift  # Remove -r from arguments
fi

# Setup virtual environment
if [[ ! -d venv ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Starting TrainPixels Controller..."
echo "Press Ctrl+C to stop"

# Check if sudo
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Run the controller script
python3 src/controller.py "$@"