#!/usr/bin/env zsh

export FLASK_APP=logos.py
export FLASK_DEBUG=1

PY_HOME=$HOME/Documents/Projects/logos
# # Make sure you're in the project directory
cd $PY_HOME
source venv/bin/activate
flask run
deactivate
