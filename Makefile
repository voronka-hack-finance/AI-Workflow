.PHONY: dev-up dev-down up down logs test sync lock context-builder-local

SERVICES := ai-workflow-service llm-intent-parser-service ai-context-builder-service analytics-service llm-response-agent-service
COMPOSE := docker compose -f docker-compose.dev.yml

sync:
	@for s in $(SERVICES); do \
		echo "==> $$s"; \
		cd $$s && uv sync && cd ..; \
	done

lock:
	@for s in $(SERVICES); do \
		echo "==> $$s"; \
		cd $$s && uv lock && cd ..; \
	done

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

logs-%:
	$(COMPOSE) logs -f $*

dev-up: up

dev-down: down

context-builder-local:
	cd ai-context-builder-service && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8012

test:
	@echo "==> packages/shared_contracts"
	@cd ai-workflow-service && uv run pytest ../packages/shared_contracts/tests -q
	@for s in $(SERVICES); do \
		echo "==> $$s"; \
		cd $$s && uv run pytest -q && cd ..; \
	done
