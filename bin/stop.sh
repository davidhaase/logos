#!/bin/sh

# @(#)stop.sh	0.1.0	10/03/2020
#
# @author       David Haase (hat tip to Jonathan Parker)
# @since        0.1.0
# @version      0.1.0
# 
# Usage:
#       stop.sh

# LOCAL PATHS
# Load the local paths
APP_HOME=${HOME}/Documents/Projects/logos

# PID and .PID FILE
# If the program spun up correctly in the start.sh script, 
# ...then, a .PID file was created with a single value: the PID
if [ -f ${APP_HOME}/run/.pid ];then
  PID=$(cat ${APP_HOME}/run/.pid)

  kill ${PID}
  
  # be sure to delete the PID file
  rm ${APP_HOME}/run/.pid
  echo "Logos has been stopped."
else
  echo "No PID file found; unable to stop Logos."
fi
