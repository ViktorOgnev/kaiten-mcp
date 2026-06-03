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

## ChatGPT smoke: temporary HTTPS tunnel

ChatGPT Developer mode supports remote MCP apps over SSE or streaming HTTP with
OAuth, No Authentication, or Mixed Authentication
([OpenAI docs](https://developers.openai.com/api/docs/guides/developer-mode)).
The direct `:8000` deploy is only a low-level server smoke; ChatGPT should use
HTTPS/OAuth.

Run the tunnel deploy:

```bash
ssh -l mcpadmin 158.160.37.91
/opt/kaiten-mcp/current/deploy/chatgpt-tunnel.sh
```

The script:

- replaces the public `:8000` shared-token container with an OAuth container in
  the same compose project;
- starts a temporary `cloudflared` quick tunnel;
- writes OAuth public URLs to `/etc/kaiten-mcp/kaiten-mcp-chatgpt.env`;
- prints a `https://*.trycloudflare.com/mcp/` URL for ChatGPT.

Use the printed URL in ChatGPT Apps settings. The trailing slash avoids an extra
HTTP redirect on MCP POST requests. The tunnel URL is temporary and can change
after container restart.

Expected unauthenticated probe:

```bash
curl -i https://<trycloudflare-host>/mcp/
```

Expected status is `401`, with a `WWW-Authenticate` header pointing to
`/.well-known/oauth-protected-resource`. That is normal: ChatGPT should use
OAuth, not a shared bearer token.

Create the ChatGPT app with:

- Connector name: `Kaiten MCP`
- Connector URL: the printed `https://*.trycloudflare.com/mcp/`
- Authentication: `OAuth`
- OAuth client type: public client / DCR when the UI asks for it

If this tunnel was previously added while `MCP_HTTP_AUTH_MODE=none`, delete or
disconnect that old ChatGPT app first. ChatGPT can keep the draft's discovered
auth mode; an old draft may continue to show `Authorization supported: None`
even after the server is switched back to OAuth.

Expected ChatGPT settings after creating the new app:

- `Authorization supported: OAuth`
- `Authorization used: OAuth` after the onboarding flow completes

During onboarding ChatGPT opens the MCP server's `/authorize` page. The user
enters their Kaiten company domain and Kaiten API key there. ChatGPT does not
send the Kaiten key in tool calls; it sends only the MCP OAuth access token.
The MCP server then looks up the session-bound Kaiten credential and calls
Kaiten with `Authorization: Bearer <kaiten-api-token>`.

Troubleshooting:

- `Authorization supported: None` means the app was created against a no-auth
  endpoint or `/readyz` still reports `auth_mode=none`; rerun the tunnel deploy
  and recreate the ChatGPT app.
- `KAITEN_TOKEN is required` means the request reached the legacy/no-auth
  Kaiten client path without an OAuth session. Do not add `KAITEN_TOKEN` to the
  public ChatGPT tunnel container; switch the MCP endpoint back to OAuth and
  reconnect the app.

To verify the same path outside the UI, run a full OAuth DCR smoke with a valid
Kaiten API key in the environment:

```bash
KAITEN_SUBDOMAIN=<company> KAITEN_TOKEN=<kaiten-api-token> \
  /opt/kaiten-mcp/current/deploy/verify-chatgpt-oauth.py \
  --mcp-url https://<trycloudflare-host>/mcp/
```

The verification script performs metadata discovery, dynamic client
registration, authorization code + PKCE exchange, MCP `initialize`, and
`tools/list`. It does not print Kaiten or OAuth tokens.
