#!/bin/bash

# Script to test inasafe-headless


HAZARD=/home/hazards/continuous_flood_20_20.asc
EXPOSURE=/home/exposures/pop_binary_raster_20_20.asc
AGGREGATION=/home/aggregations/district_osm_jakarta.shp
IMPACT=/home/impacts/raster_flood_raster_population
FUNCTION=FloodEvacuationRasterHazardFunction

docker-compose -p test build
docker-compose -p test \
    run \
    -e HAZARD=$HAZARD \
    -e EXPOSURE=$EXPOSURE \
    -e AGGREGATION=$AGGREGATION \
    -e IMPACT=$IMPACT \
    -e FUNCTION=$FUNCTION \
    inasafeheadlesstest /run-analysis.sh
