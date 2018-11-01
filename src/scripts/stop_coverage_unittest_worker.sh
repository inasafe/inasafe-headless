#!/usr/bin/env bash

if [ -z "${TASK_ALWAYS_EAGER}" ] || [ "${TASK_ALWAYS_EAGER}" = "False" ]; then
	docker-compose scale inasafe-headless-worker=0
	sleep 5
fi
