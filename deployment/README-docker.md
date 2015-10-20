# README Under construction

This README is under construction and documented the least possible way to 
set this all up and running

# Architecture

InaSAFE Headless currently running in docker to be easily deployable and run.
To build the image, simply execute this command from ```deployment``` folder

```
make build
```

The image will be built using docker-compose tools. The configuration file is
located at docker-compose.yml.

To checkout the latest InaSAFE folder, execute:

```
make checkout
```

When you run the docker-compose command over and over again. You will have
stale containers filling up your memory. To clean up stale containers:

```
make clean
```

# Testing

To test that the image can be run correctly. Execute bash script in deployment 
folder that is prefixed with __test___

# Running

To run a specific function, please refer to the test file to see the example.
For example, to get the metadata, check out ```test_metadata.sh```. See 
instructions:

```
docker-compose -p test \
    run \
    -e LAYER_FILENAME=$LAYER_FILENAME \
    inasafeheadless /run-script.sh read_metadata
```
