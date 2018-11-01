#!/usr/bin/env bash

set -e

if [ -z "${TASK_ALWAYS_EAGER}" ] || [ "${TASK_ALWAYS_EAGER}" = "False" ]; then
	for i in `seq 1 ${WORKER_SCALE}`;
	do
		make coverage-worker;
	done
fi
