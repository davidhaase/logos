#!/bin/sh

#Check if the virtual environement already exists
FILE=/logos/venv
if [ -d "$FILE" ]

# venv directory exists already, so do nothing
then
  export FLASK_APP=/logos/logos.py
  export FLASK_DEBUG=1
  source $FILE/bin/activate
  flask run
  deactivate

else
  echo "'$FILE' not found, run setup.sh first to install virtual environment"



fi
