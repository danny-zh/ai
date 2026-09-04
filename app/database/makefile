.PHONY: test-database run-database remove-database
.SHELL := /bin/bash

PYTHON ?= ../../.venv/bin/python
DATABASE_CONTAINER_NAME ?= habitdb
DATABASE_IMAGE ?= "habitdb-implementation-check:1.0.0"
PORT_MAPPING ?= "3306:3306"
MYSQL_ROOT_PASSWORD ?= "mysecretpassword"

test-database: 
	$(PYTHON) -m pytest test/test_database.py -v

run-database:remove-database
	@echo "Running database"
	@docker run -d --name $(DATABASE_CONTAINER_NAME) \
	-e MYSQL_ROOT_PASSWORD=$(MYSQL_ROOT_PASSWORD) \
	-p $(PORT_MAPPING) \
	$(DATABASE_IMAGE)

remove-database:
	@echo "Removing database $(DATABASE_CONTAINER_NAME)"
	@docker rm -f $(DATABASE_CONTAINER_NAME) || true

build-database:
	@echo "Building database image $(DATABASE_IMAGE)"
	@docker build -t $(DATABASE_IMAGE) .