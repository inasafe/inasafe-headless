#!/bin/bash

# Script to test inasafe-headless


LAYER_FILENAME=/home/hazards/continuous_flood_20_20.xml

# copying test files/

docker-compose -p test build
docker-compose -p test \
    run \
    -e LAYER_FILENAME=$LAYER_FILENAME \
    inasafeheadless /run-script.sh read_metadata
