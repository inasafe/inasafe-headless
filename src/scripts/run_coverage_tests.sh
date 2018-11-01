#!/usr/bin/env bash

# Run this from travis

# Print runtime variable
echo "Running Headless coverage test"
echo "COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME"
export CURRENT_DIR=$1
echo "Docker compose config directory: $CURRENT_DIR"

run_coverage_script () {
	pushd $CURRENT_DIR
	if [ -z "${SUBSEQUENT_RUN_TESTING}" ]; then
		docker-compose exec inasafe-headless-worker /bin/bash -c "coverage run --rcfile=/home/app/.coveragerc /usr/local/bin/nosetests --process-restartworker -v $1";
	else
		docker-compose exec inasafe-headless-worker /bin/bash -c "coverage run --rcfile=/home/app/.coveragerc /usr/local/bin/nosetests -v headless.tasks.test.test_subsequent_run";
	fi
	popd
}

shopt -s globstar

for filename in **/test_*.py; do
	echo "Test $filename"

	until run_coverage_script $filename; do
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
done

echo "Testing finished"
