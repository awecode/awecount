# Base image
FROM python:3.12.7-alpine AS backend

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache \
  libpq \
  libxslt \
  xmlsec \
  weasyprint \
  fontconfig \
  ttf-dejavu \
  bash~=5.2

# Install build dependencies temporarily and install Python packages
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  apk add --no-cache --virtual .build-deps \
  gcc \
  g++ \
  make \
  git \
  postgresql-dev \
  libc-dev \
  linux-headers \
  && uv sync --locked --no-install-project \
  && apk del .build-deps

# Copy project files
COPY manage.py .
COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --locked

# Copy bin scripts and make them executable
COPY ./bin ./bin/
RUN chmod +x ./bin/*

# Expose the port
EXPOSE 8000

# (Optional) Static files collection (uncomment if needed)
# RUN uv run manage.py collectstatic --noinput
