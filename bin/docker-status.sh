#!/bin/sh

# @(#)docker-status.sh	0.1.0	09/21/2020
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
#       docker-status.sh

APP_HOME=/flasky

if [ -f ${APP_HOME}/run/.pid ];then
  PID=$(cat ${APP_HOME}/run/.pid)
  PROC=$(/bin/ps auwwwx|grep -w "${PID}"|grep -v grep|awk '{print $1}')

  if [ -z "${PROC}" ];then
    echo "Flasky is not running as process ${PID}; the PID file must be stale"
  else
    if [ "${PID}" = "${PROC}" ];then
      echo "Flasky is running as process ${PID}."
    else
      echo "The status of Flasky is indeterminate."
    fi
  fi
else
  echo "No PID file found; Flasky is probably not running."
fi
