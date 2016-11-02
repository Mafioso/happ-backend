VERSION=minor

help:
	@echo "lint - check style with flake8"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "build - build latest docker image"
	@echo "release - build new docker image version and push it to hub"

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
