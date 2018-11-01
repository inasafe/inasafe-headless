#!/usr/bin/env bash

if [ -z "${TASK_ALWAYS_EAGER}" ] || [ "${TASK_ALWAYS_EAGER}" = "False" ]; then
	for i in `seq 1 ${WORKER_SCALE}`;
	do
		make coverage-worker-kill WORKER_ID=${i};
	done
fi
