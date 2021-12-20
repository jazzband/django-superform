#!/usr/bin/make -f

.PHONY: all
all: lint

.PHONY: lint
lint: 
	black --check .; \
	isort --diff .; \
	flake8 .; \
	mypy .
