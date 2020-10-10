#!/bin/sh

# @(#)docker-start.sh	0.1.0	09/21/2020
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
#       docker-start.sh

APP_HOME=/flasky

if [ ! -f ${APP_HOME}/run/.pid ];then
  cd ${APP_HOME}

  ${APP_HOME}/venv/bin/python3 main.py &

  echo $! > ${APP_HOME}/run/.pid
  echo "Started Flasky as process $(cat ${APP_HOME}/run/.pid)."
else
  PID=$(cat ${APP_HOME}/run/.pid)

  echo "Flasky appears to be already running as process ${PID}; unable to start it."
fi
