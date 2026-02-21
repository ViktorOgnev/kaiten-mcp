# ---- deps: Python + pip dependencies only (dev/volume-mount mode) ----
# Build: docker build --target deps -t kaiten-mcp:dev .
# Run:   docker run --rm -i -v ./src:/app/src:ro -e KAITEN_DOMAIN -e KAITEN_TOKEN kaiten-mcp:dev
FROM python:3.12-slim AS deps

WORKDIR /app

COPY pyproject.toml .
RUN mkdir -p src/kaiten_mcp && \
    touch src/kaiten_mcp/__init__.py && \
    pip install --no-cache-dir -e . && \
    rm src/kaiten_mcp/__init__.py

# Non-root user
RUN groupadd --gid 1000 mcp && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin mcp && \
    mkdir -p /app/output && \
    chown -R mcp:mcp /app

USER mcp
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["kaiten-mcp"]


# ---- baked: full image with source code (distribution mode) ----
# Build: docker build --target baked -t kaiten-mcp:latest .
# Run:   docker run --rm -i -e KAITEN_DOMAIN -e KAITEN_TOKEN kaiten-mcp:latest
FROM python:3.12-slim AS baked

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir . && \
    rm -rf /root/.cache

# Non-root user
RUN groupadd --gid 1000 mcp && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin mcp && \
    mkdir -p /app/output && \
    chown -R mcp:mcp /app

USER mcp
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["kaiten-mcp"]
