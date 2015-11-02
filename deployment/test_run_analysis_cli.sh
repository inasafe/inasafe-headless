#!/bin/bash

# Script to test inasafe-headless


HAZARD=/home/hazards/continuous_flood_20_20.asc
EXPOSURE=/home/exposures/pop_binary_raster_20_20.asc
AGGREGATION=/home/aggregations/district_osm_jakarta.shp
IMPACT=/home/impacts/raster_flood_raster_population.tif
FUNCTION=FloodEvacuationRasterHazardFunction

# copying test files

cp ../src/inasafe/safe/test/data/hazard/continuous_flood_20_20.* ../hazards/
cp ../src/inasafe/safe/test/data/exposure/pop_binary_raster_20_20.* ../exposures/
cp ../src/inasafe/safe/test/data/boundaries/district_osm_jakarta.* ../aggregations/

docker-compose -p test build
docker-compose -p test \
    run \
    inasafeheadless \
    /run-script.sh inasafe "--hazard=$HAZARD --exposure=$EXPOSURE --impact-function=$FUNCTION --report-template= --output-file=$IMPACT"
