# ---- base: shared Python environment and package dependencies ----
FROM python:3.12-slim AS base-deps

WORKDIR /app

COPY pyproject.toml .
RUN mkdir -p src/kaiten_mcp && \
    touch src/kaiten_mcp/__init__.py && \
    pip install --no-cache-dir -e . && \
    rm src/kaiten_mcp/__init__.py

RUN groupadd --gid 1000 mcp && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin mcp && \
    mkdir -p /app/output && \
    chown -R mcp:mcp /app

USER mcp
ENV PYTHONUNBUFFERED=1


# ---- deps-stdio: dev image with source mounted from host ----
FROM base-deps AS deps-stdio
ENTRYPOINT ["kaiten-mcp"]


# ---- deps: backward-compatible alias for stdio dev image ----
FROM deps-stdio AS deps


# ---- deps-http: dev image with source mounted from host ----
FROM base-deps AS deps-http
EXPOSE 8000
ENTRYPOINT ["kaiten-mcp-http"]


# ---- baked-base: full image with source code ----
FROM python:3.12-slim AS baked-base

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir . && \
    rm -rf /root/.cache

RUN groupadd --gid 1000 mcp && \
    useradd --uid 1000 --gid 1000 --no-create-home --shell /usr/sbin/nologin mcp && \
    mkdir -p /app/output && \
    chown -R mcp:mcp /app

USER mcp
ENV PYTHONUNBUFFERED=1


# ---- baked-http: self-contained HTTP image ----
FROM baked-base AS baked-http
EXPOSE 8000
ENTRYPOINT ["kaiten-mcp-http"]


# ---- baked-stdio: self-contained stdio image ----
FROM baked-base AS baked-stdio
ENTRYPOINT ["kaiten-mcp"]


# ---- baked: backward-compatible alias for stdio baked image ----
FROM baked-stdio AS baked
