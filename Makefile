WHITE=\033[m
RED=\033[1;31m
GREEN=\033[1;32m
YELLOW=\033[1;33m

VERSION=minor

help:
	@echo "lint - check style with flake8"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "build - build latest docker image"
	@echo "release - build new docker image version and push it to hub; also create tag on git commit"
	@echo "deploy - deploy latest docker image on server"

lint:
	flake8 happ tests

test-all:
	py.test

coverage:
	py.test --cov-report term-missing --cov=happ

build:
	bin/build.sh

release:
	bin/release.sh $(VERSION)

deploy:
	@echo "$(YELLOW)[ copying conf files ]$(WHITE)"
	scp -r conf/prod $(USER)@$(HOST):/home/happ/conf
	scp docker-compose.prod.yml $(USER)@$(HOST):/home/happ
	scp docker-compose.base.yml $(USER)@$(HOST):/home/happ
	@echo "$(YELLOW)[ stoping server ]$(WHITE)"
	ssh $(USER)@$(HOST) 'docker-compose -f docker-compose.prod.yml stop'
	@echo "$(YELLOW)[ pulling new image ]$(WHITE)"
	ssh $(USER)@$(HOST) 'docker pull askhatomarov/happ:latest'
	@echo "$(YELLOW)[ starting server ]$(WHITE)"
	ssh $(USER)@$(HOST) 'docker-compose -f docker-compose.prod.yml up -d'
	@echo "$(GREEN)[ everything is OK ]$(WHITE)"
