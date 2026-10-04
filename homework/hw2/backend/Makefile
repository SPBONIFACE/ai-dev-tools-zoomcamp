.PHONY: run test install

install:
	uv sync

run:
	uv run uvicorn app.main:app --reload --port 8000

test:
	uv run pytest
