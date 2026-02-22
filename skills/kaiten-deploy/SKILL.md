---
name: kaiten-deploy
description: Deploy Kaiten MCP server with guided setup wizard
version: 2.0.0
---

# Kaiten MCP Server — Interactive Deployment Wizard

This skill is an interactive wizard. At every decision point, use the `AskUserQuestion` tool to present choices. Never assume — always ask.

## Security Invariant

API keys are **NEVER** baked into Docker images. Verified by:
- `.dockerignore` excludes `.env` and `.env.*`
- Dockerfile has no `COPY .env` or `ENV KAITEN_*`
- All modes receive credentials **only at runtime** (env_file, -e flags, or load_dotenv)

## Step 1: Auto-Detection (silent)

Run ALL checks in parallel (no user interaction):

```bash
# 1. Find kaiten-mcp source directory
Glob("**/pyproject.toml") -> check for name="kaiten-mcp" -> $SOURCE_DIR

# 2. Check existing Docker images
Bash("docker images kaiten-mcp --format '{{.Repository}}:{{.Tag}}' 2>/dev/null")

# 3. Check existing venv
Glob("$SOURCE_DIR/.venv/bin/kaiten-mcp") if $SOURCE_DIR found

# 4. Check existing MCP registration
Bash("claude mcp list 2>/dev/null | grep -i kaiten")

# 5. Read .env if found
Read("$SOURCE_DIR/.env") if exists
```

Store all findings for use in subsequent steps.

## Step 2: Existing Registration Check

**If MCP server `kaiten` is already registered**, use `AskUserQuestion`:

```
AskUserQuestion:
  question: "Kaiten MCP is already registered ({scope}). What would you like to do?"
  header: "MCP Status"
  options:
    - label: "Reconfigure"
      description: "Remove current registration and set up from scratch"
    - label: "Switch account"
      description: "Change Kaiten credentials only (edit .env, no re-registration)"
    - label: "Cancel"
      description: "Keep current setup, do nothing"
```

- **Reconfigure**: run `claude mcp remove kaiten`, then continue to Step 3.
- **Switch account**: jump directly to Step 5 (Credentials).
- **Cancel**: stop, inform user that no changes were made.

**If NOT registered**, proceed to Step 3.

## Step 3: Choose Run Mode

Use `AskUserQuestion`:

```
AskUserQuestion:
  question: "How do you want to run the Kaiten MCP server?"
  header: "Run mode"
  options:
    - label: "Docker dev (Recommended)"
      description: "Source mounted via volume — code changes apply instantly. Best for developers."
    - label: "Docker baked"
      description: "Everything in the image, self-contained. Best for end users who just want 246 tools."
    - label: "Local Python"
      description: "Install to venv, no Docker needed. Requires Python 3.11+."
```

If existing image/venv was detected in Step 1, mention it in the description (e.g. "Existing image detected: kaiten-mcp:dev").

Store as `$MODE` = `docker-dev` | `docker-baked` | `python`.

## Step 4: Choose Scope

Use `AskUserQuestion`:

```
AskUserQuestion:
  question: "Where should the MCP server be available?"
  header: "Scope"
  options:
    - label: "This project only (Recommended)"
      description: "MCP server available only when working in this directory"
    - label: "All projects (global)"
      description: "MCP server available everywhere in Claude Code"
```

Store as `$SCOPE`: first option = omit `-s` flag (default project), second option = `-s user`.

## Step 5: Credentials

### If `.env` already exists with values

Use `AskUserQuestion`:

```
AskUserQuestion:
  question: "Found .env with KAITEN_DOMAIN={domain}. Use these credentials?"
  header: "Credentials"
  options:
    - label: "Yes, use existing"
      description: "Keep current domain and API token from .env"
    - label: "Enter new credentials"
      description: "I want to connect to a different Kaiten account"
```

### If no `.env`, or user chose "Enter new credentials"

Use `AskUserQuestion` for domain:

```
AskUserQuestion:
  question: "Enter your Kaiten company subdomain (the 'xxx' part of xxx.kaiten.ru):"
  header: "Domain"
  options:
    - label: "Type subdomain"
      description: "Just the subdomain, e.g. 'mycompany' — not the full URL"
    - label: "I have the full URL"
      description: "Paste full URL like https://mycompany.kaiten.ru — domain will be extracted"
```

Then ask the user to provide the actual value. Validate:
- Strip `https://`, `.kaiten.ru`, `.kaiten.io` if pasted as full URL
- Must be non-empty, no dots, no slashes

Use `AskUserQuestion` for token:

```
AskUserQuestion:
  question: "Enter your Kaiten API token:"
  header: "API Token"
  options:
    - label: "I have a token"
      description: "Paste your API token (Settings → My Profile → API tokens → Create)"
    - label: "How to get a token?"
      description: "Open Kaiten → Settings → My Profile → API tokens → Create token"
```

If "How to get a token?" — explain the steps, then ask again.

Write validated values to `$SOURCE_DIR/.env`:
```bash
# Create .env from template if needed
cp $SOURCE_DIR/.env.example $SOURCE_DIR/.env  # if .env doesn't exist
# Write KAITEN_DOMAIN=value and KAITEN_TOKEN=value
```

### After saving credentials, always inform:

```
Credentials saved to .env.

How accounts work in Kaiten:
- API token is tied to your email, not the company
- Multiple organizations on same email → same token, just change KAITEN_DOMAIN
- Different email → different token, change both KAITEN_DOMAIN and KAITEN_TOKEN
- To switch later: edit .env → restart Claude Code (/exit then claude)
- Docker Compose mode: no MCP re-registration needed when switching
```

## Step 6: Source Location

If `$SOURCE_DIR` was auto-detected in Step 1:

```
AskUserQuestion:
  question: "Kaiten MCP source found at {$SOURCE_DIR}. Use this location?"
  header: "Source"
  options:
    - label: "Yes, use {$SOURCE_DIR}"
      description: "Detected kaiten-mcp project at this path"
    - label: "Use a different path"
      description: "I want to specify another directory"
```

If not detected or user chose different path — ask for absolute path, then validate:
- `{path}/pyproject.toml` exists
- Contains `name = "kaiten-mcp"`

## Step 7: Build & Register

Show the user what will happen before executing:

```
Ready to set up Kaiten MCP:
  Mode:   {$MODE}
  Scope:  {$SCOPE}
  Domain: {$DOMAIN}
  Source: {$SOURCE_DIR}

Executing...
```

### Mode: docker-dev

```bash
# Build deps-only image
docker compose --project-directory $SOURCE_DIR build kaiten-mcp-dev

# Register (NO -e flags — credentials from .env via env_file)
claude mcp add kaiten \
  [-s user] \
  -- docker compose --project-directory $SOURCE_DIR run --rm -T kaiten-mcp-dev
```

### Mode: docker-baked

```bash
# Build full image
docker compose --project-directory $SOURCE_DIR build kaiten-mcp

# Register (NO -e flags)
claude mcp add kaiten \
  [-s user] \
  -- docker compose --project-directory $SOURCE_DIR run --rm -T kaiten-mcp
```

### Mode: python

```bash
# Create venv and install
python3 -m venv $SOURCE_DIR/.venv
$SOURCE_DIR/.venv/bin/pip install -e $SOURCE_DIR

# Parse KAITEN_DOMAIN and KAITEN_TOKEN from $SOURCE_DIR/.env

# Register (with -e flags — load_dotenv CWD is unpredictable)
claude mcp add kaiten \
  [-s user] \
  -e KAITEN_DOMAIN=$DOMAIN \
  -e KAITEN_TOKEN=$TOKEN \
  -- $SOURCE_DIR/.venv/bin/kaiten-mcp
```

## Step 8: Verify & Finish

```bash
claude mcp list
```

Final message:

```
Setup complete! Kaiten MCP server is registered.

To activate 246 tools:
  1. Type /exit
  2. Run `claude` again
  3. Try: "Show me my Kaiten user info"

Quick reference:
  - Switch company (same email): edit KAITEN_DOMAIN in .env → restart Claude Code
  - Switch account (different email): edit both values in .env → restart Claude Code
  - Docker Compose mode: no MCP re-registration needed for credential changes
  - Update code (dev mode): restart Claude Code — changes apply instantly
  - Update code (baked mode): make build → restart Claude Code
```

## Account Switching Flow

When user asks to switch accounts (outside of initial setup), use `AskUserQuestion`:

```
AskUserQuestion:
  question: "How is the new Kaiten account different from current?"
  header: "Account"
  options:
    - label: "Different company, same email"
      description: "API token stays the same — only KAITEN_DOMAIN changes"
    - label: "Different email entirely"
      description: "Both KAITEN_DOMAIN and KAITEN_TOKEN need to change"
```

### Same email, different company

1. Read current `.env` to find $SOURCE_DIR
2. Edit `.env` — change only `KAITEN_DOMAIN`
3. Inform: "Restart Claude Code (/exit then claude). Token stays the same, no re-registration needed."

### Different email

1. Read current `.env` to find $SOURCE_DIR
2. Ask for new `KAITEN_DOMAIN` and `KAITEN_TOKEN` (same as Step 5)
3. Write to `.env`
4. For Docker Compose: "Restart Claude Code. No re-registration needed."
5. For docker run / python: `claude mcp remove kaiten` → re-register with new `-e` values.

## Anti-patterns (NEVER DO THIS)

- **NEVER** `claude mcp remove` + `claude mcp add` just to change credentials in Compose mode — edit `.env` instead
- **NEVER** use `-t` flag with `docker run` — TTY breaks MCP stdio protocol
- **NEVER** use `docker compose run` without `-T`
- **NEVER** hardcode credentials in `claude mcp add -e` for Docker Compose — Compose reads `.env` via `env_file`

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|---------|
| Server registered but tools not visible | Tools load at session start | Restart Claude Code: /exit then claude |
| `command not found: timeout` | TTY in docker compose | Add `-T` flag to `docker compose run` |
| `MCP server kaiten already exists` | Already registered | `claude mcp remove kaiten` then re-register |
| Docker build fails | Network or cache issue | `docker build --no-cache --target deps .` |
| `externally-managed-environment` | System Python protected | Use venv: `python3 -m venv .venv` |
| Server hangs / no response | TTY allocated | Remove `-t`, ensure only `-i` is used |
| Credentials not picked up (Compose) | `.env` not in project dir | Ensure `.env` is in kaiten-mcp root; use `--project-directory` |
| Credentials not picked up (python) | CWD mismatch | Use `-e` flags in `claude mcp add` |

## Update Paths

| What changed | docker-dev | docker-baked | python |
|-------------|-----------|-------------|--------|
| Source code | Restart Claude Code | `make build` + restart | Restart Claude Code |
| Dependencies | `make dev-build` + restart | `make build` + restart | `pip install -e .` + restart |
| Credentials (Compose) | Edit `.env` → restart | Edit `.env` → restart | N/A |
| Credentials (python) | N/A | N/A | `claude mcp remove` + re-register |
| Scope | `claude mcp remove kaiten -s $OLD` + re-register | same | same |
