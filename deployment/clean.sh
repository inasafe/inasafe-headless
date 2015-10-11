#!/bin/bash

CONTAINERS=$(docker ps -a | grep inasafeheadless_run | awk '{print $(NF)}')

echo "Removing containers"

for c in $CONTAINERS
do
    docker rm $c
done
