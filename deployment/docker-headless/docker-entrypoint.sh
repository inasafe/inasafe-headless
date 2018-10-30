#!/usr/bin/env bash

# Wait run xvfb
while [ -z  "$(pidof /usr/bin/Xvfb)" ]; do
  start-stop-daemon --start -b -x /usr/bin/Xvfb ${DISPLAY}
  sleep 5
done

cp -n /home/app/headless/celeryconfig_sample.py /home/app/headless/celeryconfig.py
echo "Config file copied"

if [ $# -eq 2 ] && [ $1 = "prod" ] && [ $2 = "inasafe-headless-worker" ]; then
    /usr/local/bin/celery -A headless.celery_app worker -l info -Q inasafe-headless -n inasafe-headless.%h
elif [ $# -eq 1 ] && [ $1 = "dev" ]; then
	/usr/sbin/sshd -D
fi

exec "$@"
