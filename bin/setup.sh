#!/bin/sh

# The setup.sh installs the Python virtual requirement if it doesn't exist already

#Check if the virtual environement already exists
FILE=../venv
if [ -d "$FILE" ]

# venv directory exists already, so do nothing
then
  echo "'$FILE' directory already exists, cancelling set-up"

else
  echo "Starting set-up, creating VENV directory and virtual environment"

  # Create a virtual environment
  python3 -m venv $FILE

  # Best-practice to upgrade pip
  source $FILE/bin/activate
  pip install --upgrade pip

  #Install the requirement packages
  pip install -r ../requirements.txt
  deactivate

fi
