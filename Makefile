IMAGE       := kaiten-mcp
SRC_DIR     := $(shell pwd)/src
VENV_DIR    := $(shell pwd)/.venv

# --- Dev mode (volume-mount, instant code changes) ---

.PHONY: dev-build
dev-build:  ## Build deps-only image for development
	docker build --target deps -t $(IMAGE):dev .

.PHONY: dev-run
dev-run: dev-build  ## Run MCP server with source mounted (dev mode)
	docker run --rm -i \
		--read-only --tmpfs /tmp:noexec,nosuid,size=64m \
		--security-opt=no-new-privileges:true --cap-drop=ALL \
		-v $(SRC_DIR):/app/src:ro \
		-e KAITEN_DOMAIN -e KAITEN_TOKEN \
		$(IMAGE):dev

# --- Baked mode (distribution, self-contained) ---

.PHONY: build
build:  ## Build full image for distribution
	docker build --target baked -t $(IMAGE):latest .

.PHONY: run
run: build  ## Run baked MCP server
	docker run --rm -i \
		--read-only --tmpfs /tmp:noexec,nosuid,size=64m \
		--security-opt=no-new-privileges:true --cap-drop=ALL \
		-e KAITEN_DOMAIN -e KAITEN_TOKEN \
		$(IMAGE):latest

# --- HTTP mode (remote deployment) ---

.PHONY: http-dev-build
http-dev-build:  ## Build deps-only HTTP image for development
	docker build --target deps-http -t $(IMAGE)-http:dev .

.PHONY: http-dev-run
http-dev-run: http-dev-build  ## Run HTTP MCP server with source mounted (dev mode)
	docker run --rm \
		--read-only --tmpfs /tmp:noexec,nosuid,size=64m \
		--security-opt=no-new-privileges:true --cap-drop=ALL \
		-v $(SRC_DIR):/app/src:ro \
		-p $${MCP_HTTP_PORT:-8000}:$${MCP_HTTP_PORT:-8000} \
		-e KAITEN_DOMAIN -e KAITEN_TOKEN -e MCP_AUTH_TOKEN \
		-e MCP_HTTP_HOST=$${MCP_HTTP_HOST:-0.0.0.0} \
		-e MCP_HTTP_PORT=$${MCP_HTTP_PORT:-8000} \
		-e MCP_HTTP_BASE_PATH=$${MCP_HTTP_BASE_PATH:-/mcp} \
		$(IMAGE)-http:dev

.PHONY: http-build
http-build:  ## Build full HTTP image for remote deployment
	docker build --target baked-http -t $(IMAGE)-http:latest .

.PHONY: http-run
http-run: http-build  ## Run baked HTTP MCP server
	docker run --rm \
		--read-only --tmpfs /tmp:noexec,nosuid,size=64m \
		--security-opt=no-new-privileges:true --cap-drop=ALL \
		-p $${MCP_HTTP_PORT:-8000}:$${MCP_HTTP_PORT:-8000} \
		-e KAITEN_DOMAIN -e KAITEN_TOKEN -e MCP_AUTH_TOKEN \
		-e MCP_HTTP_HOST=$${MCP_HTTP_HOST:-0.0.0.0} \
		-e MCP_HTTP_PORT=$${MCP_HTTP_PORT:-8000} \
		-e MCP_HTTP_BASE_PATH=$${MCP_HTTP_BASE_PATH:-/mcp} \
		$(IMAGE)-http:latest

# --- Local Python (venv, no Docker) ---

.PHONY: venv
venv:  ## Create venv and install in editable mode
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -e .

.PHONY: local-run
local-run:  ## Run MCP server from local venv
	$(VENV_DIR)/bin/kaiten-mcp

# --- Testing (always Docker) ---

.PHONY: test
test:  ## Run all tests with coverage
	docker compose -f tests/docker-compose.test.yml up --build test-overseer

.PHONY: lint
lint:  ## Run linters (ruff + mypy)
	docker compose -f tests/docker-compose.test.yml run --rm lint

.PHONY: lint-fix
lint-fix:  ## Auto-fix lint issues
	docker compose -f tests/docker-compose.test.yml run --rm lint-fix

# --- Utilities ---

.PHONY: clean
clean:  ## Remove build artifacts and Docker images
	rm -rf build/ dist/ src/*.egg-info
	docker rmi $(IMAGE):dev $(IMAGE):latest $(IMAGE)-http:dev $(IMAGE)-http:latest 2>/dev/null || true

.PHONY: help
help:  ## Show available targets
	@echo "kaiten-mcp build targets:"
	@echo ""
	@echo "  Dev mode (volume-mount, instant code changes):"
	@echo "    dev-build     Build deps-only image"
	@echo "    dev-run       Run with source mounted from host"
	@echo ""
	@echo "  Baked mode (distribution, self-contained):"
	@echo "    build         Build full image with source baked in"
	@echo "    run           Run baked image"
	@echo ""
	@echo "  Local Python (no Docker):"
	@echo "    venv          Create venv and install package"
	@echo "    local-run     Run MCP server from venv"
	@echo ""
	@echo "  HTTP mode (remote deployment):"
	@echo "    http-dev-build Build deps-only HTTP image"
	@echo "    http-dev-run   Run HTTP server with source mounted from host"
	@echo "    http-build     Build baked HTTP image"
	@echo "    http-run       Run baked HTTP image"
	@echo ""
	@echo "  Testing:"
	@echo "    test          Run all tests with coverage (Docker)"
	@echo "    lint          Run ruff + mypy (Docker)"
	@echo "    lint-fix      Auto-fix lint issues (Docker)"
	@echo ""
	@echo "  Utilities:"
	@echo "    clean         Remove build artifacts and images"

.DEFAULT_GOAL := help
