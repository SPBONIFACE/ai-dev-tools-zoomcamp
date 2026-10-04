.PHONY: run run-backend run-frontend test install

run: run-backend

run-backend:
	cd backend && make run

run-frontend:
	cd frontend && npm run dev

test:
	cd backend && make test

install:
	cd backend && make install
	cd frontend && npm install
