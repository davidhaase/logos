#!/usr/bin/env zsh

export FLASK_APP=logos.py
export FLASK_DEBUG=1

source venv/bin/activate
flask run
deactivate
