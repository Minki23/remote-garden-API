SERVICE ?= .
IMAGE_NAME ?= $(notdir $(SERVICE))
REGISTRY ?= your-docker-org
TAG ?= latest
IMAGE = $(REGISTRY)/$(IMAGE_NAME):$(TAG)

SERVICES = admin_app agent_app api_app mqtt_broker_app csr_signer_app mock_mqtt_app

.PHONY: build
build:
	@echo ">>> Building image: $(IMAGE)"
ifeq ($(SERVICE), .)
	docker build -t $(IMAGE) .
else
	docker build -f $(SERVICE)/Dockerfile -t $(IMAGE) .
endif

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
		docker build -f $$s/Dockerfile -t $(REGISTRY)/$$s:$(TAG) .; \
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

.PHONY: help
help:
	@echo ""
	@echo "Usage: make [target] [VARIABLE=value]"
	@echo ""
	@echo "Targets:"
	@echo "  build              Build one Docker image"
	@echo "  push               Push one Docker image"
	@echo "  deploy             Build + Push one Docker image"
	@echo "  build-all          Build all services: $(SERVICES)"
	@echo "  push-all           Push all services"
	@echo "  deploy-all         Build + Push all services"
	@echo ""
	@echo "Variables:"
	@echo "  SERVICE       Path to service directory (default: .)"
	@echo "  REGISTRY      Docker registry/org (default: your-docker-org)"
	@echo "  TAG           Image tag (default: latest)"
	@echo ""
	@echo "Examples:"
	@echo "  make build SERVICE=admin_app REGISTRY=myregistry TAG=v1.0"
	@echo "  make deploy SERVICE=api_app TAG=v1.0"
	@echo "  make build-all TAG=development"
	@echo "  make deploy-all REGISTRY=prod-registry TAG=v2.0"
	@echo ""

.DEFAULT_GOAL := help