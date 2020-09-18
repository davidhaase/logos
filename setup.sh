#!/usr/bin/env zsh

# Create a virtual environment
python3 -m venv ./venv

# Best-practice to upgrade pip
source venv/bin/activate
pip install --upgrade pip

# Install the requirement packages
pip install -r requirements.txt
