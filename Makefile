.PHONY: install run test migrate lint docker-build docker-up docker-down

install:
	uv sync

run:
	uv run python manage.py runserver

test:
	uv run python manage.py test

migrate:
	uv run python manage.py migrate

lint:
	uvx ruff check .

docker-build:
	docker compose build

docker-up:
	touch db.sqlite3
	docker compose up -d

docker-down:
	docker compose down
