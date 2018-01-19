SHELL := /bin/bash

PROJECT_ID := headless

default: build deploy status

build:
	@echo
	@echo "--------------------------"
	@echo "Building"
	@echo "--------------------------"
	@docker-compose -p $(PROJECT_ID) build

ansible-check:
	@echo "Check ansible command"
	@ansible -i ansible/development/hosts all -m ping
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml --check --list-tasks --list-hosts $(ANSIBLE_ARGS)

setup-ansible:
	@echo "Setup configurations using ansible"
	@ansible-playbook -i ansible/development/hosts ansible/development/site.yml -v $(ANSIBLE_ARGS)

up:
	@echo
	@echo "--------------------------"
	@echo "Bringing up fresh instances"
	@echo "--------------------------"
	@docker-compose -p $(PROJECT_ID) up -d

worker-shell:
	@docker-compose -p $(PROJECT_ID) exec inasafe-headless-worker /bin/bash

worker-logs:
	@docker-compose -p $(PROJECT_ID) logs -f --tail=30 inasafe-headless-worker

shakemap-monitor-shell:
	@docker-compose -p $(PROJECT_ID) exec inasafe-shakemap-monitor /bin/bash

shakemap-monitor-logs:
	@docker-compose -p $(PROJECT_ID) logs -f --tail=30 inasafe-shakemap-monitor

package-tests:
	@docker-compose -p $(PROJECT_ID) exec inasafe-headless-worker python -m unittest discover -s headless -v

coverage-tests:
	@-docker-compose -p $(PROJECT_ID) exec inasafe-headless-worker coverage run --branch --source=headless -m unittest discover -s headless -v
	@echo "Copying coverage files"
	@docker-compose -p $(PROJECT_ID) exec inasafe-headless-worker cp .coverage headless/.coverage

down:
	@docker-compose -p $(PROJECT_ID) down

status:
	@echo
	@echo "--------------------------"
	@echo "Show status of all containers"
	@echo "--------------------------"
	@docker-compose -p $(PROJECT_ID) ps
