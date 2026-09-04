.PHONY: run-ollama rm-ollama build-copilot-image run-copilot rm-copilot rm-copilot-image test-database up-app down-app logs-app up-habit-tracker down-habit-tracker logs-habit-tracker test-backend
.SHELL := /bin/bash

OLLAMA_PORT=11434
COPILOT_IMAGE=copilot-cli:latest
COPILOT_CONTAINER=copilot-cli
PYTHON ?= .venv/bin/python

test-database:
	$(PYTHON) -m pytest app/database/test/test_database.py -v

up-app:
	docker compose up --build --detach

down-app:
	docker compose down

logs-app:
	docker compose logs --follow

up-habit-tracker: up-app

down-habit-tracker: down-app

logs-habit-tracker: logs-app

test-backend:
	$(PYTHON) -m pytest app/backend/test -v

run-ollama: rm-ollama
	@echo "Running Ollama locally at port $(OLLAMA_PORT)"
	@docker run --rm -d \
	-v /home/${USER}/personal/k8s-admin/certs/:/usr/local/share/ca-certificates:ro \
	-p $(OLLAMA_PORT):11434 \
	-v $(PWD)/ollama:/root/.ollama \
	--name ollama \
	ollama/ollama:latest

rm-ollama:
	@echo "Removing Ollama container"
	@docker ps -aq -f name=ollama | xargs -r docker rm -f

build-copilot-image:
	@echo "Building Copilot image $(COPILOT_IMAGE)"
	@docker build -t $(COPILOT_IMAGE) -f $(PWD)/copilot/Dockerfile $(PWD)

run-copilot: rm-copilot
	@echo "Running Copilot container $(COPILOT_CONTAINER)"
	@docker run -it \
	--name $(COPILOT_CONTAINER) \
	-v $(PWD)/copilot/.copilot:/root/.copilot \
	-v $(PWD):/work \
	-w /work \
	--net host \
	-v /var/run/docker.sock:/var/run/docker.sock \
	$(COPILOT_IMAGE)

rm-copilot:
	@echo "Removing Copilot container"
	@docker ps -aq -f name=$(COPILOT_CONTAINER) | xargs -r docker rm -f

rm-copilot-image: rm-copilot
	@echo "Removing Copilot image $(COPILOT_IMAGE)"
	@docker image inspect $(COPILOT_IMAGE) >/dev/null 2>&1 && docker rmi -f $(COPILOT_IMAGE) || true


start-docker:
	@eco