.PHONY: help dev clean coverage check serve test test-staging test-dev superuser migrate create-db refresh-db todos token bench pytest \
		aws_ecr_update_auth_credentials aws_ecr_production_image_update aws_ecr_uat_image_update aws_eb_uat_deploy aws_eb_production_deploy \
		docker_build_local docker_build_uat docker_build_production docker_run_local

DJANGO_COMMAND = python manage.py
PYTEST_CONFIG = -s -v --disable-warnings --cov-report  term-missing

help:
	@echo "Please use 'make <target>' where <target> is one of"
	@egrep '^(.+)\:.*?#+\ *(.+)' ${MAKEFILE_LIST} | column -t -c 2 -s '#'

run: ## To run project locally
	@echo "--> \033[0;32mUping in the port 8000\033[0m"
	docker-compose up

down: ## To run project locally
	@echo "--> \033[0;32mUping in the port 8000\033[0m"
	docker-compose down

build: ## To build with docker-compose
	export DOCKER_BUILDKIT=1;docker-compose build

build-no-cache:  ## To build with docker-compose and without cache
	export DOCKER_BUILDKIT=1;docker-compose build --no-cache

install-requirements:  ## To install requirements
	pip install -r requirements/dev.txt
	pip install -r requirements/tests.txt
	pip install -r requirements/base.txt

pip-compile:
	@echo "--> Removing .txt files"
	rm -f requirements/base.txt
	rm -f requirements/tests.txt
	rm -f requirements/dev.txt

	@echo "--> Running pip-compile"
	DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose run start-api bash -c	" \
	pip-compile requirements/dev.in && \
	pip-compile requirements/tests.in && \
	pip-compile requirements/base.in"

test: ## To test application and coverage
	@echo "--> \033[0;32mUping the services to run tests\033[0m"
	docker-compose run start-api pytest $(path) $(PYTEST_CONFIG)
	docker-compose down

test-no-cache: ## To test application and coverage no cache tests
	docker-compose run start-api bash -c "rm -rf .pytest_cache"
	@echo "--> \033[0;32mUping the services to run tests without cache\033[0m"
	docker-compose run start-api pytest $(path) $(PYTEST_CONFIG)
	docker-compose down

style-check: ## To check code-styling
	@echo "--> \033[0;32mChecking the code style...\033[0m"
	docker-compose run start-api black -S -t py38 -l 79 --check . --exclude '/(\.git|venv|env|build|dist)/'
	docker-compose down

safe: ## To check code dependencies
	@echo "--> \033[0;32mChecking the code dependencies...\033[0m"
	docker-compose run start-api safety check -i 52495

shell: ## To access shell conected in your local database
	@echo "--> \033[0;32mStarting shell...\033[0m"
	docker-compose run start-api $(DJANGO_COMMAND) shell

migrations:
	@echo "--> \033[0;32mCreating Migrations\033[0m"
	docker-compose run start-api $(DJANGO_COMMAND) makemigrations

migrate:
	@echo "--> \033[0;32mMigrating...\033[0m"
	docker-compose run start-api $(DJANGO_COMMAND) migrate

setup: ## To setup local environment
	@echo "--> \033[0;32mSetuping...\033[0m"

superuser: ## To create super user
	@echo "--> \033[0;32mIntroduce your local credentials:\033[0m"
	docker-compose run start-api $(DJANGO_COMMAND) createsuperuser

deploy: ## To deploy
	zappa update $(env)
