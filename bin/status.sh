#!/bin/sh

# @(#)status.sh	0.1.0	10/03/2020
#
# @author       David Haase (hat tip to Jonathan Parker)
# @since        0.1.0
# @version      0.1.0
# 
# Usage:
#       status.sh

# Turn off color coding in grep for macOS

export GREP_OPTIONS=

APP_HOME=${HOME}/Documents/Projects/logos

if [ -f ${APP_HOME}/run/.pid ];then
  PID=$(cat ${APP_HOME}/run/.pid)
  PROC=$(/bin/ps auwwwx|grep -w "${PID}"|grep -v grep|awk '{print $2}')

  if [ -z "${PROC}" ];then
    echo "Logos is not running as process ${PID}; the PID file must be stale"
  else
    if [ "${PID}" = "${PROC}" ];then
      echo "Logos is running as process ${PID}."
    else
      echo "The status of Logos is indeterminate."
    fi
  fi
else
  echo "No PID file found; Logos is probably not running."
fi
