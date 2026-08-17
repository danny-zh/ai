.PHONY: build-opencode-image start-opencode-agent stop-opencode-agent attach-opencode-agent
SHELL := /bin/bash

DOCKER_FOLDER=./docker
AGENT_NAME=opencode_agent
AGENT_IMAGE="opencode:1.0.0"

build-opencode-image:
	@echo "Building ${AGENT_IMAGE} opencode image from ${DOCKER_FOLDER}"
	@echo docker build -t ${AGENT_IMAGE} ${DOCKER_FOLDER}
	docker build -t ${AGENT_IMAGE} ${DOCKER_FOLDER}

start-opencode-agent: stop-opencode-agent
	@echo "Starting opencode image from ${DOCKER_FOLDER}"
	@echo "docker run -d --name ${AGENT_NAME} ${AGENT_IMAGE} sleep 3600"
	docker run -d --name ${AGENT_NAME} ${AGENT_IMAGE} "sleep 3600"

stop-opencode-agent:
	@echo "Stopping opencode agent ${AGENT_NAME}"
	@echo "docker rm -f ${AGENT_NAME} || true"
	@docker rm -f ${AGENT_NAME} || true

attach-opencode-agent:
	@echo "Attaching opencode agent ${AGENT_NAME}"
	@echo docker exec -it ${AGENT_NAME} bash
	docker exec -it ${AGENT_NAME} bash
