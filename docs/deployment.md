# Deployment

This deployment path is designed for a public repository: the server pulls a
branch from GitHub over HTTPS and stores runtime configuration outside the
checkout.

## First smoke deploy: direct port

- Host: `mcpadmin@158.160.37.91`
- Source ref: `origin/remote-server-transport`
- Application directory: `/opt/kaiten-mcp/current`
- Runtime env file: `/etc/kaiten-mcp/kaiten-mcp.env`
- Public endpoint: `http://158.160.37.91:8000/mcp`
- Auth mode: `shared`

The port-only deploy is a single-tenant smoke test. It uses one server-side
Kaiten API token and one shared MCP bearer token. Do not use OAuth onboarding on
plain HTTP, because users would enter Kaiten API keys without HTTPS.

## First-time host bootstrap

Open inbound TCP `8000` in the cloud firewall/security group.

Then connect to the host and run the bootstrap script from the public branch:

```bash
ssh -l mcpadmin 158.160.37.91
curl -fsSL https://raw.githubusercontent.com/ViktorOgnev/kaiten-mcp/remote-server-transport/deploy/bootstrap-host.sh \
  -o /tmp/bootstrap-host.sh
bash /tmp/bootstrap-host.sh
```

Edit the server env file:

```bash
sudoedit /etc/kaiten-mcp/kaiten-mcp.env
```

Minimum smoke config:

```dotenv
MCP_HTTP_PORT=8000
MCP_HTTP_AUTH_MODE=shared
MCP_AUTH_TOKEN=<random-token>
KAITEN_SUBDOMAIN=yourcompany
KAITEN_TOKEN=<kaiten-api-token>
MCP_ALLOWED_ORIGINS=
LOG_LEVEL=INFO
```

Use `KAITEN_BASE_URL` instead of `KAITEN_SUBDOMAIN` only for non-standard
Kaiten hosts.

## Regular deploy

Deploys are intentionally explicit. Log in to the server and run the checked-in
deploy script:

```bash
ssh -l mcpadmin 158.160.37.91
/opt/kaiten-mcp/current/deploy/deploy.sh
```

The script:

- refuses dirty server checkouts;
- fetches and fast-forwards `remote-server-transport` from GitHub;
- validates that port deploy auth is `shared`;
- requires `KAITEN_TOKEN` and `MCP_AUTH_TOKEN` in the server env file;
- rebuilds the `baked-http` image;
- restarts the HTTP app;
- verifies health and unauthenticated `/mcp` returning `401`.

If a smoke deploy must be rolled back, revert or fix `remote-server-transport`
in GitHub and run the same deploy command again.

## Manual checks

After deploy, these should pass from any machine that can reach the server:

```bash
curl -fsS http://158.160.37.91:8000/healthz
curl -fsS http://158.160.37.91:8000/readyz
curl -sS -o /tmp/kaiten-mcp.json -w "%{http_code}\n" http://158.160.37.91:8000/mcp
curl -sS -o /tmp/kaiten-mcp-auth.json -w "%{http_code}\n" \
  -H "Authorization: Bearer $MCP_AUTH_TOKEN" \
  http://158.160.37.91:8000/mcp
```

Expected `/readyz` auth mode is `shared`; expected unauthenticated `/mcp` status
is `401`; expected authenticated MCP transport probe status is `400`, `405`, or
`406`.

## Later production mode

For multi-user usage, switch to HTTPS and OAuth onboarding:

- point a real domain to `158.160.37.91`;
- open inbound TCP `80` and `443`;
- use `deploy/docker-compose.prod.yml` and `deploy/.env.production.example`;
- run with `MCP_HTTP_AUTH_MODE=oauth`.

In OAuth mode, each user enters their own Kaiten company domain and API key on
the HTTPS onboarding page. Those credentials live only in process memory until
the session expires, so a deploy/restart requires users to reconnect.
