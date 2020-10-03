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
LOG_OUT=${APP_HOME}/logs/logos.out
LOG_ERR=${APP_HOME}/logs/logos.err

echo "Started Logos as process $(cat ${APP_HOME}/run/.pid)."

# PID and .PID FILE
# A .pid file is created when the app spins up
# The .pid file contains simply the PID of the current app
# ...it gets checked by the status.sh script
# ...and gets removed by the stop.sh script


# First, confirm that the PID FILE doesn't already exist
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
