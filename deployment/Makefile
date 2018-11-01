SHELL := /bin/bash

PROJECT_ID := headless

export COMPOSE_PROJECT_NAME=headless

default: build deploy status

build:
	@echo
	@echo "--------------------------"
	@echo "Building"
	@echo "--------------------------"
	@docker-compose build

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
	@docker-compose up -d

worker-shell:
	@docker-compose exec inasafe-headless-worker /bin/bash

worker-logs:
	@docker-compose logs -f --tail=30 inasafe-headless-worker

package-tests:
	@docker-compose exec inasafe-headless-worker python -m unittest discover -s headless -v

coverage-worker-kill:
	@docker kill --signal=SIGINT headless_inasafe-headless-worker_run_${WORKER_ID}
	@sleep 5
	@docker rm headless_inasafe-headless-worker_run_${WORKER_ID}

coverage-worker:
	@docker-compose run --rm -d inasafe-headless-worker coverage run --rcfile=/home/app/.coveragerc /usr/local/bin/celery -A headless.celery_app worker -l info -Q inasafe-headless -n inasafe-headless.%h -P solo

coverage-tests:
	@-docker-compose exec inasafe-headless-worker coverage run -m unittest discover -s headless -v

travis-coverage-tests:
	@-docker-compose exec `bash <(curl -s https://codecov.io/env)` inasafe-headless-worker coverage run --branch --source=headless -m unittest discover -s headless -v && codecov

check-flake8:
	@flake8 ../src/

down:
	@docker-compose down

rm:
	@docker-compose rm

kill:
	@docker-compose kill

status:
	@echo
	@echo "--------------------------"
	@echo "Show status of all containers"
	@echo "--------------------------"
	@docker-compose ps

clean-test-output:
	@echo "Clean test output in src/headless/tasks/test/data/result/"
	@rm -rf ../src/headless/tasks/test/data/result/*
