.PHONY: build-opencode-image start-opencode-agent stop-opencode-agent attach-opencode-agent
SHELL := /bin/bash

DOCKER_FOLDER=./docker
AGENT_NAME=opencode_agent
AGENT_IMAGE="opencode:1.0.0"
LOCAL_WORK_DIR=./workspace

build-opencode-image:
	@echo "Building ${AGENT_IMAGE} opencode image from ${DOCKER_FOLDER}"
	@echo docker build -t ${AGENT_IMAGE} ${DOCKER_FOLDER}
	docker build -t ${AGENT_IMAGE} ${DOCKER_FOLDER}

start-opencode-agent: stop-opencode-agent
	@echo "Starting opencode image from ${DOCKER_FOLDER}"
	@mkdir -p ${LOCAL_WORK_DIR}
	@mkdir -p ${LOCAL_WORK_DIR}/.opencode
	@mkdir -p ${LOCAL_WORK_DIR}/.local/share/opencode
	@echo "docker run -d --name ${AGENT_NAME} ${AGENT_IMAGE} sleep 3600"
	docker run -d \
	--mount type=bind,source=${LOCAL_WORK_DIR},target=/work \
	--mount type=bind,source=${LOCAL_WORK_DIR}/.opencode,target=/root/.config/opencode \
	--mount type=bind,source=${LOCAL_WORK_DIR}/.local/share/opencode,target=/root/.local/share/opencode \
	--name ${AGENT_NAME} ${AGENT_IMAGE} "sleep 3600"

stop-opencode-agent:
	@echo "Stopping opencode agent ${AGENT_NAME}"
	@echo "docker rm -f ${AGENT_NAME} || true"
	@docker rm -f ${AGENT_NAME} || true

attach-opencode-agent:
	@echo "Attaching opencode agent ${AGENT_NAME}"
	@echo docker exec -it ${AGENT_NAME} bash
	docker exec -it ${AGENT_NAME} bash
