#!/bin/bash

# Remove virtual environment first
[[ -d venv ]] && rm -r venv
[[ -d src/__pycache__ ]] && rm -r src/__pycache__

# Setting up virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Installing requirements..."
pip install -r requirements.txt
echo