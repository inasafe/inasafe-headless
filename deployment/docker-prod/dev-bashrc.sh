#!/bin/bash

source /home/inasafe/src/inasafe/run-env-linux.sh /usr

# variable export

export DISPLAY=:99

export INASAFE_SOURCE_DIR=/home/inasafe/src/inasafe
export InaSAFEQGIS=$INASAFE_SOURCE_DIR
export AMQP_HOST=rabbitmq
export DB_USERNAME=docker
export DB_PASS=docker
export C_FORCE_ROOT=True
export INASAFE_HEADLESS_BROKER_HOST=amqp://guest:guest@rabbitmq:5672//
export INASAFE_HEADLESS_DEPLOY_OUTPUT_DIR=/home/web
export INASAFE_HEADLESS_DEPLOY_OUTPUT_URL=http://outputhost/

cd $INASAFE_SOURCE_DIR
