.PHONY: dev-up dev-down test sync lock

SERVICES := ai-workflow-service llm-intent-parser-service ai-context-builder-service analytics-service llm-response-agent-service

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
	docker compose -f docker-compose.dev.yml up --build -d

down:
	docker compose -f docker-compose.dev.yml down

test:
	@for s in $(SERVICES); do \
		echo "==> $$s"; \
		cd $$s && uv run pytest -q && cd ..; \
	done
