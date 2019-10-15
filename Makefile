.PHONY: setup clean lint test
	SHELL := /bin/bash
PIP_ENV:=$(shell pipenv --venv)
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

 ifeq ($(OS),Windows_NT)
	    UNAME := Windows
	else
	    UNAME := $(shell uname -s)
	endif

shell:
	    @pipenv shell

setup:
	    @pipenv --three install --dev

pipenv-lock:
	    @pipenv update
		    @pipenv lock -r > requirements.txt

format:
	    @pipenv run black ./sample/*.py
		    @pipenv run black ./test/*.py

lint:
	    @pipenv run black --check OpenEIT/**/*.py

test: setup
	    -@$(PIP_ENV)/bin/coverage run -m unittest -v

test-by-name:
	    -@$(PIP_ENV)/bin/coverage run -m unittest $(TEST) -v

coverage:
	    @$(PIP_ENV)/bin/coverage report -m

clean:
	    @rm -r $(PIP_ENV)
