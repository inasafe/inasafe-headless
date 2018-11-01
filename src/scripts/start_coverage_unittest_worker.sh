#!/usr/bin/env bash

set -e

if [ -z "${TASK_ALWAYS_EAGER}" ] || [ "${TASK_ALWAYS_EAGER}" = "False" ]; then
	echo "Command: ${HEADLESS_COMMAND}"
	docker-compose scale inasafe-headless-worker=${WORKER_SCALE}
	sleep 5
	docker-compose logs inasafe-headless-worker
fi
