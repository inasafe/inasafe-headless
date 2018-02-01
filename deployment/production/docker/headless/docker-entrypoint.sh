#!/usr/bin/env bash

# Run xvfb
start-stop-daemon --start -b -x /usr/bin/Xvfb ${DISPLAY}

cp -n /home/app/headless/celeryconfig_sample.py /home/app/headless/celeryconfig.py

/usr/local/bin/celery -A headless.celery_app worker -l info -Q inasafe-headless -n inasafe-headless.%h
