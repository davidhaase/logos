#!/bin/sh

# @(#)stop.sh	0.1.0	10/03/2020
#
# @author       David Haase (hat tip to Jonathan Parker)
# @since        0.1.0
# @version      0.1.0
# 
# Usage:
#       stop.sh

APP_HOME=${HOME}/Documents/Projects/logos

if [ -f ${APP_HOME}/run/.pid ];then
  PID=$(cat ${APP_HOME}/run/.pid)

  kill ${PID}
  rm ${APP_HOME}/run/.pid
  echo "Logos has been stopped."
else
  echo "No PID file found; unable to stop Logos."
fi
