SERVICE ?= .
IMAGE_NAME ?= $(notdir $(SERVICE))
REGISTRY ?= your-docker-org
TAG ?= latest
IMAGE = $(REGISTRY)/$(IMAGE_NAME):$(TAG)

SERVICES = admin_app agent_app api_app mqtt_broker_app csr_signer_app mock_mqtt_app

.PHONY: build
build:
	@echo ">>> Building image: $(IMAGE)"
	docker build -t $(IMAGE) $(SERVICE)

.PHONY: push
push:
	@echo ">>> Pushing image: $(IMAGE)"
	docker push $(IMAGE)

.PHONY: deploy
deploy: build push
	@echo ">>> Image deployed: $(IMAGE)"

.PHONY: build-all
build-all:
	@for s in $(SERVICES); do \
		echo ">>> Building image: $(REGISTRY)/$$s:$(TAG)"; \
		docker build -t $(REGISTRY)/$$s:$(TAG) $$s; \
	done

.PHONY: push-all
push-all:
	@for s in $(SERVICES); do \
		echo ">>> Pushing image: $(REGISTRY)/$$s:$(TAG)"; \
		docker push $(REGISTRY)/$$s:$(TAG); \
	done

.PHONY: deploy-all
deploy-all: build-all push-all
	@echo ">>> All images deployed"

.PHONY: run
run:
	@echo ">>> Starting docker compose from delivery_app"
	cd delivery_app && docker compose build --no-cache && docker compose up --force-recreate

.PHONY: run-detached
run-detached:
	@echo ">>> Starting docker compose from delivery_app in background"
	cd delivery_app && docker compose up -d --build --force-recreate

.PHONY: stop
stop:
	@echo ">>> Stopping docker compose from delivery_app"
	cd delivery_app && docker compose down

.PHONY: help
help:
	@echo ""
	@echo "Usage: make [target] [VARIABLE=value]"
	@echo ""
	@echo "Targets:"
	@echo "  build          Build one Docker image"
	@echo "  push           Push one Docker image"
	@echo "  deploy         Build + Push one Docker image"
	@echo "  build-all      Build all services: $(SERVICES)"
	@echo "  push-all       Push all services"
	@echo "  deploy-all     Build + Push all services"
	@echo "  run            Run docker-compose from delivery_app"
	@echo "  run-detached   Run docker-compose from delivery_app in background"
	@echo "  stop           Stop docker-compose from delivery_app"
	@echo ""
	@echo "Variables:"
	@echo "  SERVICE   Path to service directory (default: .)"
	@echo "  REGISTRY  Docker registry/org (default: your-docker-org)"
	@echo "  TAG       Image tag (default: latest)"
	@echo ""

.DEFAULT_GOAL := help