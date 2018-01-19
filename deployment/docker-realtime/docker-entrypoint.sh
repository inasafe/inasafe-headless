#!/usr/bin/env bash

# Run xvfb
start-stop-daemon --start -b -x /usr/bin/Xvfb ${DISPLAY}
# Source InaSAFE environment
source /run-env-linux.sh /usr


if [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-headless-worker" ]; then
	cp -n /home/app/headless/celeryconfig_sample.py /home/app/headless/celeryconfig.py
    /usr/local/bin/celery -A headless.celery_app worker -l info -Q inasafe-headless -n inasafe-headless.%h
elif [ $# -eq 1 ] && [ $1 = "dev" ]; then
	/usr/sbin/sshd -D
fi
