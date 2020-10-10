#!/bin/sh

# @(#)docker-launch.sh	0.1.0	09/21/2020
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
#       docker-launch.sh

sig_handler()
{
	echo "Handling SIGTERM in parent process."
	echo "Invoking stop for child process ${PID}..."
        bin/stop.sh
}

trap sig_handler SIGTERM

echo "Parent process is starting a child process..."

bin/start.sh

PID=$(cat run/.pid)

echo "Now waiting on child process ${PID} and a SIGTERM."

while [ -e /proc/${PID} ]; do sleep 1;done
