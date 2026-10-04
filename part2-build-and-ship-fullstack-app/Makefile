.PHONY: run test install frontend run-frontend help

help:
	@echo "Available commands:"
	@echo "  make run          Run the FastAPI backend on port 8091"
	@echo "  make test         Run backend test suite with pytest"
	@echo "  make install      Install backend dependencies with uv"
	@echo "  make frontend     Run the frontend development server"
	@echo "  make run-frontend Alias for make frontend"

run:
	cd backend && uv run uvicorn backend.main:app --reload --port 8091

test:
	cd backend && uv run pytest -v

install:
	cd backend && uv sync

frontend:
	cd frontend && pnpm dev

run-frontend: frontend
