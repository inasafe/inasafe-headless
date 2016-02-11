# README Under construction

This README is under construction and documented the least possible way to 
set this all up and running

# Architecture

InaSAFE Headless currently running in docker to be easily deployable and test.
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

The following is a typical test environment workflow

```
# deploy basic image
make deploy
# run tests using CELERY_ALWAYS_EAGER=True
make tests
# run celery-worker for headless package
make celery-worker
# view logs of celery-worker
make celery-worker-logs
# run tests using CELERY_ALWAYS_EAGER=False
# which means, the tasks will be executed by celery-worker
# so make sure it was running first
make celery-tests
# kill all instances
make kill
```

Celery-Flower monitoring tool is also installed and running after you execute 
```make deploy```. Access ```http://your-docker-machine-ip:62002``` via web browser 
to view active broker and worker.

# Testing in Pycharm

You can easily setup a testing environment in pycharm.

1. Run ```make deploy``` this will setup a working environment
2. Setup a remote python interpreter to the docker container, with:
   - ssh host: your docker machine ip
   - ssh port: 62000
   - user: root
   - password: docker
   - interpreter location: /usr/bin/python
3. Setup Tools > Deployment > Configuration. Create path mappings from local's ```src/inasafe``` to remote ```/home/inasafe/src``` 
4. Setup python configuration for Celery Worker:
   - Use #2 Remote Python interpreter previously setup
   - Fill environment variable with something like this:
   
     ```
INASAFE_HEADLESS_DB_USERNAME=docker
PYTHONPATH=/usr/share/qgis/python:/usr/share/qgis/python/plugins:/home/realtime/src/inasafe
INASAFE_LOCALE=id
C_FORCE_ROOT=True
INASAFE_HEADLESS_DEPLOY_OUTPUT_DIR=/home/web
INASAFE_HEADLESS_DB_PASS=docker
InaSAFEQGIS=/home/inasafe/src/inasafe
INASAFE_HEADLESS_DEPLOY_OUTPUT_URL=http://docker-inasafe-headless:62001/
INASAFE_HEADLESS_BROKER_HOST=amqp://guest:guest@rabbitmq:5672//
DISPLAY=:99
PYTHONUNBUFFERED=1
INASAFE_SOURCE_DIR=/home/inasafe/src/inasafe
     ```
   - Fill script with ```/usr/local/bin/celery```
   - Fill script parameter with ```-A headless.celery_app worker -l info -Q inasafe-headless```
   - Set Working Dir to ```src/inasafe``` directory

You can also create similar environment for Nosetests. This way, you can easily run tests and debug it from inside Pycharm
