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

kill:
	@echo
	@echo "------------------------------------------------------------------"
	@echo "Kill instance in production mode"
	@echo "------------------------------------------------------------------"
	@docker-compose -p $(PROJECT_ID) kill
