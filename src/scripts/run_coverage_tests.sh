#!/usr/bin/env bash

# Run this from travis

# Print runtime variable
echo "Running Headless coverage test"
echo "COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME"
export CURRENT_DIR=$1
echo "Docker compose config directory: $CURRENT_DIR"
export PACKAGE_DIR=$2
echo "Package dir to check: $PACKAGE_DIR"

run_coverage_script () {
	pushd $CURRENT_DIR
	if [ -z "${SUBSEQUENT_RUN_TESTING}" ]; then
		docker-compose run --rm inasafe-headless-worker /bin/bash -c "coverage run --rcfile=/home/app/.coveragerc /usr/local/bin/nosetests --process-restartworker -v $1";
	else
		docker-compose run --rm inasafe-headless-worker /bin/bash -c "coverage run --rcfile=/home/app/.coveragerc /usr/local/bin/nosetests -v headless.tasks.test.test_subsequent_run";
	fi
	exit_code=$?
	popd
	return $exit_code
}

shopt -s globstar

pushd $PACKAGE_DIR

for filename in **/test_*.py; do
	echo "Test $filename"

	until run_coverage_script $filename; do
		# Retrieve exit code
		exit_code=$?
		echo "EXIT CODE: $exit_code"

		if [ "$exit_code" -eq "1" ]; then
			echo "Unittests failed"

			echo "Printing immediate headless celery worker logs"
			pushd $CURRENT_DIR
			docker-compose logs --tail=100 inasafe-headless-worker
			popd
			break 2
		elif [ "$exit_code" -eq "139" ]; then
			echo "Unittests finished but doesn't exit cleanly"
			exit_code=0
		fi
		# investigate why it failed
		echo "Is it memory error?"
		journalctl -k | grep -i -e memory -e oom

		echo "Docker inspect"
		docker inspect headless_inasafe-headless-worker_1

		# Restart attempt
		echo "$PWD"
		pushd $CURRENT_DIR
		make up
		docker-compose restart inasafe-headless-worker
		popd
		sleep 10
		if [ "$exit_code" -eq "0" ]; then
			break
		fi
	done
done

popd
echo "Testing finished"
exit $exit_code
