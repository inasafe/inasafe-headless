#!/usr/bin/env bash

# Run this from travis

# Print runtime variable
echo "Running Headless coverage test"
echo "COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME"

run_coverage_script() {
	if [ -z "${SUBSEQUENT_RUN_TESTING}" ]; then
		docker-compose exec inasafe-headless-worker /bin/bash -c "coverage run --rcfile=/home/app/.coveragerc -m unittest discover -v -s headless";
	else
		docker-compose exec inasafe-headless-worker /bin/bash -c "coverage run --rcfile=/home/app/.coveragerc -m unittest headless.tasks.test.test_subsequent_run";
	fi
}

until run_coverage_script; do
	# Retrieve exit code
	exit_code=$?
	echo "EXIT CODE: $exit_code"

	if [ "$exit_code" -eq "1" ]; then
		echo "Unittests failed"
		exit 1
	elif [ "$exit_code" -eq "139" ]; then
		echo "Unittests finished but doesn't exit cleanly"
		exit 0
	fi
	# investigate why it failed
	echo "Is it memory error?"
	journalctl -k | grep -i -e memory -e oom

	echo "Docker inspect"
	docker inspect headless_inasafe-headless-worker_1

	# Restart attempt
	echo "$PWD"
	make up
	sleep 10
done

echo "Testing finished"
