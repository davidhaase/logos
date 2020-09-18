#!/usr/bin/env zsh

FLASK_APP=logos.py
FLASK_DEBUG=1

PY_HOME=$HOME/Documents/Projects/logos
# Make sure you're in the project directory
cd $PY_HOME
./venv/bin/python3 demo.py
