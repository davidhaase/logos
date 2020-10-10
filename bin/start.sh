#!/bin/sh

# @(#)start.sh	0.1.0	10/03/2020
#
# @author       David Haase (hat tip to Jonathan Parker)
# @since        0.1.0
# @version      0.1.0
# 
# Usage:
#       start.sh


# LOCAL PATHS
# Load the local paths
APP_HOME=${HOME}/Documents/Projects/logos
# APP_HOME="${PWD%/*}"
LOG_OUT=${APP_HOME}/logs/logos.out
LOG_ERR=${APP_HOME}/logs/logos.err
VIRT_ENV=${APP_HOME}/venv
#Check if the virtual environement already exists
if [ -d "$VIRT_ENV" ]

# venv directory exists already, so do nothing
then
  echo "'$VIRT_ENV' directory already exists, no set-up required"

else
  echo "venv dir not found; setting up virtual environement"

  # Create a virtual environment
  python3 -m venv $VIRT_ENV

  # Best-practice to upgrade pip
  source $VIRT_ENV/bin/activate
  pip install --upgrade pip

  #Install the requirement packages
  pip install -r ${APP_HOME}/requirements.txt --use-feature=2020-resolver
  deactivate

fi



echo "Started Logos as process $(cat ${APP_HOME}/run/.pid)."

# PID and .PID FILE
# A .pid file is created when the app spins up
# The .pid file contains simply the PID of the current app
# ...it gets checked by the status.sh script
# ...and gets removed by the stop.sh script


# First, confirm that the PID FILE doesn't already exist
# if [ ! -d ${APP_HOME}/run/ ];then
#   mkdir ${APP_HOME}/run/
# fi

if [ ! -f ${APP_HOME}/run/.pid ];then
  
  # Then, clear out the logs for each job if they already exist
  if [ -f ${LOG_OUT} ];then
    rm ${LOG_OUT}
  fi

  if [ -f ${LOG_ERR} ];then
    rm ${LOG_ERR}
  fi

  # Now run the app
  cd ${APP_HOME}
  export FLASK_APP=${APP_HOME}/logos.py
  export FLASK_DEBUG=1
  
  # ...&-command to run in the background
  ${APP_HOME}/venv/bin/flask run 1>${LOG_OUT} 2>${LOG_ERR} &

  # ...$! returns the PID
  echo $! > ${APP_HOME}/run/.pid
  
  # ...cat "concatentate the text from [filename]"
  echo "Started Logos as process $(cat ${APP_HOME}/run/.pid)."

# A PID file exists already, is it already running?
else
  PID=$(cat ${APP_HOME}/run/.pid)

  echo "Logos appears to be already running as process ${PID}; unable to start it."
fi
