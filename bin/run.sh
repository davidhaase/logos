#!/bin/sh

#Check if the virtual environement already exists
FILE=../venv # use this if using Terminal
if [ -d "$FILE" ]

# venv directory exists already, so do nothing
then
  export FLASK_APP=../logos.py # use this if using Terminal
  export FLASK_DEBUG=1
  export TRANSLATOR_MODEL_LOCATION=AWS
  source $FILE/bin/activate 
  flask run
  deactivate

else
  echo "'$FILE' not found, run setup.sh first to install virtual environment"
fi
