#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_FILE="${ENV_FILE:-/etc/kaiten-mcp/kaiten-mcp.env}"
DEPLOY_REF="${DEPLOY_REF:-remote-server-transport}"
PROJECT_NAME="${PROJECT_NAME:-kaiten-mcp}"
COMPOSE_FILE="${COMPOSE_FILE:-$REPO_DIR/deploy/docker-compose.port.yml}"
PUBLIC_HOST="${PUBLIC_HOST:-158.160.37.91}"

fail() {
	echo "ERROR: $*" >&2
	exit 1
}

docker_cmd() {
	if docker info >/dev/null 2>&1; then
		docker "$@"
	elif sudo -n docker info >/dev/null 2>&1; then
		sudo docker "$@"
	else
		fail "Docker is not available to this user. Run deploy/bootstrap-host.sh first."
	fi
}

compose() {
	docker_cmd compose \
		--project-name "$PROJECT_NAME" \
		--env-file "$ENV_FILE" \
		-f "$COMPOSE_FILE" \
		"$@"
}

show_debug() {
	echo
	echo "Docker compose status:"
	compose ps || true
	echo
	echo "Recent service logs:"
	compose logs --tail=120 || true
}

trap 'echo "Deploy failed." >&2; show_debug >&2' ERR

[[ -f "$ENV_FILE" ]] || fail "$ENV_FILE does not exist. Run deploy/bootstrap-host.sh first."
[[ -d "$REPO_DIR/.git" ]] || fail "$REPO_DIR is not a git checkout."

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

MCP_HTTP_PORT="${MCP_HTTP_PORT:-8000}"
MCP_HTTP_AUTH_MODE="${MCP_HTTP_AUTH_MODE:-shared}"

[[ "$MCP_HTTP_AUTH_MODE" == "shared" ]] || fail "Port deploy requires MCP_HTTP_AUTH_MODE=shared."
[[ -n "${MCP_AUTH_TOKEN:-}" ]] || fail "MCP_AUTH_TOKEN is required in $ENV_FILE."
[[ "$MCP_AUTH_TOKEN" != "replace-with-random-token" ]] || fail "Replace the example MCP_AUTH_TOKEN in $ENV_FILE."
[[ -n "${KAITEN_TOKEN:-}" ]] || fail "KAITEN_TOKEN is required in $ENV_FILE for shared port deploy."
[[ "$KAITEN_TOKEN" != "replace-with-kaiten-api-token" ]] || fail "Replace the example KAITEN_TOKEN in $ENV_FILE."
if [[ -z "${KAITEN_BASE_URL:-}" && -z "${KAITEN_SUBDOMAIN:-${KAITEN_DOMAIN:-}}" ]]; then
	fail "Set KAITEN_SUBDOMAIN, KAITEN_DOMAIN, or KAITEN_BASE_URL in $ENV_FILE."
fi

if ! git -C "$REPO_DIR" diff --quiet || ! git -C "$REPO_DIR" diff --cached --quiet; then
	fail "$REPO_DIR has local changes. Commit, discard, or inspect them before deploying."
fi

echo "Syncing $DEPLOY_REF from origin..."
git -C "$REPO_DIR" fetch --prune origin "$DEPLOY_REF"
if git -C "$REPO_DIR" show-ref --verify --quiet "refs/heads/$DEPLOY_REF"; then
	git -C "$REPO_DIR" checkout "$DEPLOY_REF"
else
	git -C "$REPO_DIR" checkout -b "$DEPLOY_REF" "origin/$DEPLOY_REF"
fi
git -C "$REPO_DIR" pull --ff-only origin "$DEPLOY_REF"

echo "Validating compose config..."
compose config --quiet

echo "Building and restarting services..."
compose build --pull kaiten-mcp-http
compose up -d --remove-orphans

app_container="$(compose ps -q kaiten-mcp-http)"
[[ -n "$app_container" ]] || fail "Could not find kaiten-mcp-http container."

echo "Waiting for application health..."
for _ in {1..60}; do
	health="$(docker_cmd inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$app_container")"
	if [[ "$health" == "healthy" ]]; then
		break
	fi
	sleep 2
done
[[ "$health" == "healthy" ]] || fail "Application container did not become healthy; last status: $health."

local_base_url="http://127.0.0.1:$MCP_HTTP_PORT"
public_base_url="http://$PUBLIC_HOST:$MCP_HTTP_PORT"

echo "Checking local HTTP endpoints..."
curl -fsS --retry 12 --retry-delay 5 --retry-connrefused "$local_base_url/healthz" >/dev/null
ready_json="$(curl -fsS --retry 12 --retry-delay 5 --retry-connrefused "$local_base_url/readyz")"
echo "$ready_json" | grep -q '"auth_mode":"shared"' || fail "/readyz did not report shared auth mode: $ready_json"

unauth_status="$(curl -sS -o /tmp/kaiten-mcp-unauth-mcp.json -w "%{http_code}" "$local_base_url/mcp")"
[[ "$unauth_status" == "401" ]] || fail "Unauthenticated /mcp returned HTTP $unauth_status instead of 401."

auth_status="$(
	curl -sS \
		-o /tmp/kaiten-mcp-auth-mcp.json \
		-w "%{http_code}" \
		-H "Authorization: Bearer $MCP_AUTH_TOKEN" \
		"$local_base_url/mcp"
)"
case "$auth_status" in
	400 | 405 | 406) ;;
	*) fail "Authenticated /mcp returned HTTP $auth_status; expected MCP transport probe status 400/405/406." ;;
esac

if curl -fsS --connect-timeout 5 "$public_base_url/readyz" >/dev/null; then
	echo "Public port check passed: $public_base_url/readyz"
else
	echo "WARNING: local deploy is healthy, but $public_base_url/readyz is not reachable from this host."
	echo "Open TCP $MCP_HTTP_PORT in the cloud firewall/security group if external clients cannot reach it."
fi

trap - ERR
echo "Deploy complete: $public_base_url/mcp"
