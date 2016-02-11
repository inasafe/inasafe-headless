#!/bin/bash

# Start Xvfb in separate process
start-stop-daemon --start -b -x /usr/bin/Xvfb :99

cd $INASAFE_SOURCE_DIR
source run-env-linux.sh /usr


if [ "$1" == "" ];
then
	# start flower
	flower -A headless.celery_app --port=5555 &

	# start sshd
	/usr/sbin/sshd -D
elif [ "$1" == "celery-worker" ];
then
	# start celery worker
	celery -A headless.celery_app worker -l info -Q inasafe-headless
elif [ "$1" == "tests" ];
then
	echo "Start tests without celery worker"
	export CELERY_ALWAYS_EAGER=True
	nosetests headless --with-id --verbose

elif [ "$1" == "celery-tests" ];
then
	echo "Start tests with celery worker running"
	export CELERY_ALWAYS_EAGER=False
	nosetests headless --with-id --verbose
fi
