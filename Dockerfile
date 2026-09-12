# Stage 1: Build virtual environment
FROM python:3.11-slim AS builder

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency definition files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv without installing project or dev dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Stage 2: Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Environment configuration
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AI_PROVIDER=mock \
    PATH="/app/.venv/bin:$PATH"

# Copy virtualenv from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY . /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
