#!/bin/sh

#Check if the virtual environement already exists
# FILE=/logos/venv # use this if building docker
FILE=../venv # use this if using Terminal
if [ -d "$FILE" ]

# venv directory exists already, so do nothing
then
  # export FLASK_APP=/logos/logos.py # use this if building docker
  export FLASK_APP=../logos.py # use this if using Terminal
  export FLASK_DEBUG=1
  source $FILE/bin/activate
  flask run
  deactivate

else
  echo "'$FILE' not found, run setup.sh first to install virtual environment"
fi
