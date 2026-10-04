.PHONY: run test install frontend run-frontend help compose-up compose-down test-integration e2e responder observability-up observability-down test-alert

help:
	@echo "Available commands:"
	@echo "  make run              Run the FastAPI backend with OpenTelemetry"
	@echo "  make test             Run backend test suite with pytest"
	@echo "  make install          Install backend dependencies with uv"
	@echo "  make frontend         Run the frontend development server"
	@echo "  make observability-up Start OTel Collector, Prometheus, Loki, Tempo, Grafana"
	@echo "  make observability-down Stop observability stack"
	@echo "  make responder        Start AI Incident Responder service on port 8001"
	@echo "  make test-alert       Send synthetic alert to incident responder"

run:
	cd backend && uv run uvicorn backend.main:app --reload --port 8091

test:
	cd backend && uv run pytest -v

install:
	cd backend && uv sync

frontend:
	cd frontend && pnpm dev

run-frontend: frontend

compose-up:
	docker compose up --build

compose-down:
	docker compose down

test-integration:
	cd backend && uv run pytest -v ../e2e/test_compose_integration.py

e2e:
	cd backend && uv run pytest -v ../e2e/test_two_session_e2e.py

observability-up:
	cd observability && docker compose up -d

observability-down:
	cd observability && docker compose down

responder:
	cd incident-response && ./run.sh

test-alert:
	cd incident-response && ./test_alert.sh 8001



