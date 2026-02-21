---
name: kaiten-deploy
description: Deploy Kaiten MCP server with guided setup wizard
version: 1.0.0
---

# Kaiten MCP Server Deployment

This skill guides the user through deploying the Kaiten MCP server for Claude Code. It supports three deployment modes, two scopes, and includes auto-detection of existing setups.

## Anti-patterns (NEVER DO THIS)

- **NEVER** use `-t` flag with `docker run` -- TTY breaks MCP's JSON-RPC stdio protocol
- **NEVER** bake `.env` or API tokens into Docker images -- use `-e` flags or `--env-file`
- **NEVER** use `docker compose run` without `-T` -- allocates pseudo-TTY
- **NEVER** use relative paths in `claude mcp add` -- Claude Code may launch from any CWD
- **NEVER** run `pip install` into the system Python -- always use venv

## Phase 0: Auto-Detection

Before asking questions, silently probe the environment. Run all checks in parallel:

```
1. Glob for pyproject.toml with name="kaiten-mcp" in CWD
   -> $SOURCE_DIR or null

2. docker images kaiten-mcp --format '{{.Repository}}:{{.Tag}}'
   -> existing image tags or null

3. Check for .venv/bin/kaiten-mcp relative to $SOURCE_DIR
   -> $VENV_PATH or null

4. claude mcp list 2>/dev/null | grep kaiten
   -> existing registration or null

5. Read $SOURCE_DIR/.env if found
   -> pre-filled KAITEN_DOMAIN and KAITEN_TOKEN or null
```

If MCP server is already registered, ask:

```
Kaiten MCP is already registered ({scope}, {status}).
  1. Reconfigure -- remove and set up again
  2. Cancel -- keep current setup
```

If "Reconfigure": `claude mcp remove kaiten` then continue.

## Phase 1: Choose Mode

Ask the user:

```
How do you want to run the Kaiten MCP server?

  1. Docker (dev) -- source mounted via volume, code changes are instant
     Best for: developers who edit kaiten-mcp source
     {if image found: "Existing image detected: kaiten-mcp:dev"}

  2. Docker (baked) -- everything in the image, self-contained
     Best for: end users who just want the 246 tools
     {if image found: "Existing image detected: kaiten-mcp:latest"}

  3. Local Python -- install to venv, no Docker needed
     Best for: quick setup, Python 3.11+ required
     {if venv found: "Existing venv detected"}
```

Store as `$MODE` = `docker-dev` | `docker-baked` | `python`.

## Phase 2: Choose Scope

```
Where should the MCP server be registered?

  1. Project -- only when working in {CWD}
  2. Global -- available in all projects
```

Store as `$SCOPE` = `project` | `user`.

## Phase 3: Credentials (.env file)

Credentials live in `.env`, NOT in the `claude mcp add` command. This means changing domain/token = edit `.env` + restart Claude Code. No re-registration needed.

```
# Check if .env exists
if $SOURCE_DIR/.env exists:
  "Found .env with KAITEN_DOMAIN={domain}. Use these credentials? [Y/n]"
else:
  "Create .env from template:"
  cp $SOURCE_DIR/.env.example $SOURCE_DIR/.env
  "Edit .env -- set KAITEN_DOMAIN and KAITEN_TOKEN"
```

Validate `.env` contents:
- `KAITEN_DOMAIN`: non-empty, no dots/slashes. Strip `https://` and `.kaiten.ru` if pasted.
- `KAITEN_TOKEN`: non-empty, 20+ characters.

For python mode (no Docker Compose), credentials must be passed via `-e` flags since `load_dotenv()` depends on CWD.

## Phase 4: Source Location

If `$SOURCE_DIR` detected: confirm. Otherwise ask for absolute path.
Validate: `{path}/pyproject.toml` exists and contains `name = "kaiten-mcp"`.

## Phase 5: Execute

### Mode: docker-dev (RECOMMENDED)

Docker Compose reads `.env` automatically. No `-e` flags in `claude mcp add`.

```bash
# Step 1: Build deps-only image
docker compose --project-directory $SOURCE_DIR build kaiten-mcp-dev

# Step 2: Register MCP server (NO -e flags -- credentials from .env)
claude mcp add kaiten \
  -s $SCOPE \
  -- docker compose --project-directory $SOURCE_DIR run --rm -T kaiten-mcp-dev
```

After code changes: just restart Claude Code. No rebuild needed.
After dependency changes (pyproject.toml): `docker compose --project-directory $SOURCE_DIR build kaiten-mcp-dev`.
After credential changes: edit `.env` → restart Claude Code. No re-registration.

### Mode: docker-baked

Docker Compose reads `.env` automatically.

```bash
# Step 1: Build full image
docker compose --project-directory $SOURCE_DIR build kaiten-mcp

# Step 2: Register MCP server (NO -e flags)
claude mcp add kaiten \
  -s $SCOPE \
  -- docker compose --project-directory $SOURCE_DIR run --rm -T kaiten-mcp
```

After code changes: `docker compose --project-directory $SOURCE_DIR build kaiten-mcp` then restart Claude Code.
After credential changes: edit `.env` → restart Claude Code.

### Mode: python

For venv mode, credentials are passed via `-e` (since `load_dotenv()` CWD is unpredictable):

```bash
# Step 1: Create venv and install
python3 -m venv $SOURCE_DIR/.venv
$SOURCE_DIR/.venv/bin/pip install -e $SOURCE_DIR

# Step 2: Read credentials from .env
# Parse KAITEN_DOMAIN and KAITEN_TOKEN from $SOURCE_DIR/.env

# Step 3: Register MCP server
claude mcp add kaiten \
  -s $SCOPE \
  -e KAITEN_DOMAIN=$DOMAIN \
  -e KAITEN_TOKEN=$TOKEN \
  -- $SOURCE_DIR/.venv/bin/kaiten-mcp
```

After code changes: just restart Claude Code (editable install picks up changes).
After dependency changes: `$SOURCE_DIR/.venv/bin/pip install -e $SOURCE_DIR`.

## Phase 6: Verify

```bash
claude mcp list
```

Tell user:
```
Setup complete. Restart Claude Code to activate 246 Kaiten tools:
  1. Type /exit
  2. Run `claude` again

After restart, try: "Show me my Kaiten user info"
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|---------|
| Server registered but tools not visible | Tools load at session start | Restart Claude Code: /exit then claude |
| `command not found: timeout` | TTY enabled in docker compose | Add `-T` flag to `docker compose run` |
| `MCP server kaiten already exists` | Already registered | `claude mcp remove kaiten` then re-register |
| Docker build fails | Network or cache issue | `docker build --no-cache --target deps .` |
| `externally-managed-environment` | System Python protected | Use venv: `python3 -m venv .venv` |
| Server hangs / no response | TTY allocated (`-t` flag) | Remove `-t`, ensure only `-i` is used |
| Permission denied in container | Non-root user + read-only mount | Expected behavior for security; output dir needs separate mount |

## Update Paths

| What changed | docker-dev | docker-baked | python |
|-------------|-----------|-------------|--------|
| Source code | Restart Claude Code | `make build` + restart | Restart Claude Code |
| Dependencies | `make dev-build` + restart | `make build` + restart | `pip install -e .` + restart |
| Credentials (Compose) | Edit `.env` → restart Claude Code | same | N/A |
| Credentials (python) | N/A | N/A | `claude mcp remove` + re-register with new `-e` |
| Scope | `claude mcp remove kaiten -s $OLD` + re-register | same | same |

## Docker Security Flags

All Docker commands use hardened security flags:

| Flag | Purpose |
|------|---------|
| `--read-only` | Container filesystem is read-only |
| `--tmpfs /tmp:noexec,nosuid,size=64m` | Writable temp only, no executables |
| `--security-opt=no-new-privileges:true` | No privilege escalation |
| `--cap-drop=ALL` | Drop all Linux capabilities |
| `-v src:/app/src:ro` | Source code read-only (dev mode) |
| `-i` (no `-t`) | Stdin open, no TTY |

## Makefile Shortcuts

If the user is in the kaiten-mcp directory, they can use Make:

```bash
make help        # Show all targets
make dev-build   # Build deps-only image
make build       # Build full image
make venv        # Create venv + install
make test        # Run tests (Docker)
make lint        # Run linters (Docker)
```
