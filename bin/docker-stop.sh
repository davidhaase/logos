#!/bin/sh

# @(#)docker-stop.sh	0.1.0	09/21/2020
#
# Copyright (c) Penguin Random House, LLC
# 400 Hahn Road
# Westminster, MD 21157 U.S.A.
# All Rights Reserved.
#
# @author       Jonathan Parker
# @since        0.1.0
# @version      0.1.0
# 
# Usage:
#       docker-stop.sh

APP_HOME=/flasky

if [ -f ${APP_HOME}/run/.pid ];then
  PID=$(cat ${APP_HOME}/run/.pid)

  kill ${PID}
  rm ${APP_HOME}/run/.pid
  echo "Flasky has been stopped."
else
  echo "No PID file found; unable to stop Flasky."
fi
