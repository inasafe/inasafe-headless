SHELL := /bin/bash
PROJECT_ID := inasafeheadless

# ----------------------------------------------------------------------------
#    P R O D U C T I O N     C O M M A N D S
# ----------------------------------------------------------------------------

default: deploy

clean:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Cleaning stale containers"
	@echo "------------------------------------------------------------------"
	@`pwd`/clean.sh

build:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Building in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) build

checkout:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Checkout latest InaSAFE develop code"
	@echo "------------------------------------------------------------------"
	@`pwd`/setup.sh checkout develop

deploy: clean build
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Deploy in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) up -d inasafeheadless
	@docker-compose -p $(PROJECT_ID) up -d outputhost

shell:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Shelling in production mode"
	@echo "------------------------------------------------------------------"
	@docker exec -it inasafeheadless_inasafeheadless_1 /bin/bash

tests:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running test in eager mode"
	@echo "------------------------------------------------------------------"
	@docker exec -it inasafeheadless_inasafeheadless_1 /start-dev.sh tests

celery-tests:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Running test in celery worker mode"
	@echo "Don't forget to run make celery-worker first"
	@echo "------------------------------------------------------------------"
	docker exec -it inasafeheadless_inasafeheadless_1 /start-dev.sh celery-tests

celery-worker:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Run celery worker in production mode"
	@echo "------------------------------------------------------------------"
	# @docker-compose -p $(PROJECT_ID) run -d inasafeheadless /start-dev.sh celery-worker
	@docker-compose -p $(PROJECT_ID) up -d worker

celery-worker-logs:
	@echo
	@echo "--------------------------"
	@echo "Viewing shakemaps monitor logs"
	@echo "Latest 10 lines, and follow logs"
	@echo "--------------------------"
	# @docker logs -f --tail=10 $(PROJECT_ID)_inasafeheadless_run_1
	@docker logs -f --tail=10 $(PROJECT_ID)_worker_1

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Kill instance in production mode"
	@echo "------------------------------------------------------------------"
	@for i in $$(docker ps -a | grep "inasafeheadless_inasafeheadless_run" | cut -f1 -d" "); \
		do docker rm -f $$i; \
	done
	@docker-compose -p $(PROJECT_ID) kill
	@docker-compose -p $(PROJECT_ID) rm
