# BUILD STAGE
# version pinned for making sure that each instance is reproducible
FROM python:3.14.4-slim-bookworm AS builder

# Copy UV binary from official image
# version pinned for making sure that each instance is reproducible
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

# The container will always run in this working dir
WORKDIR /app

# UV Docker optimizations
# Tells uv to pre-compile python at build time, without it python would compile at import level which makes the first request slower
ENV UV_COMPILE_BYTECODE=1
# Avoid hardlinks (default of uv) and ensures that the files are actually copied
ENV UV_LINK_MODE=copy
# Tells uv to use python from the base image instead downloading its own
ENV UV_PYTHON_DOWNLOADS=0

# Install dependencies first (cached if unchanged). The last arg "/." points to the "/app"
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# Copy app code and install project
COPY . ./
RUN uv sync --locked --no-dev

# PRODUCTION STAGE
FROM python:3.14.4-slim-bookworm

WORKDIR /app

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy app and dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /app /app

ENV PATH="/app/.venv/bin:$PATH"
# Allows print statements and logs
ENV PYTHONUNBUFFERED=1
# For local testing but it will be overwritten in prod
ENV PORT=8080

# exec replaces shell so fastapi receives SIGTERM for clean shutdown
# there no worker flags because cloud run scales by adding more containers not by adding more workers within a container
# A single process per container is more efficient (faster cold starts and simpler memory management. The auto scaler in
# cloud run will spin up more containers as it is needed.
CMD ["/bin/sh", "-c", "exec fastapi run --host 0.0.0.0 --port \"$PORT\" --proxy-headers --forwarded-allow-ips '*'"]

