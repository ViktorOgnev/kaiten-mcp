#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

BASE_ENV_FILE="${BASE_ENV_FILE:-/etc/kaiten-mcp/kaiten-mcp.env}"
ENV_FILE="${ENV_FILE:-/etc/kaiten-mcp/kaiten-mcp-chatgpt.env}"
DEPLOY_REF="${DEPLOY_REF:-remote-server-transport}"
PROJECT_NAME="${PROJECT_NAME:-kaiten-mcp}"
COMPOSE_FILE="${COMPOSE_FILE:-$REPO_DIR/deploy/docker-compose.chatgpt-tunnel.yml}"

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
	compose logs --tail=160 || true
}

write_tunnel_env() {
	local public_base_url="$1"
	local tmp_file
	tmp_file="$(mktemp)"
	chmod 600 "$tmp_file"
	cat >"$tmp_file" <<EOF
LOG_LEVEL=${LOG_LEVEL:-INFO}
MCP_HTTP_AUTH_MODE=oauth
MCP_REQUIRED_SCOPES=${MCP_REQUIRED_SCOPES:-kaiten:tools}
MCP_ALLOWED_ORIGINS=${MCP_ALLOWED_ORIGINS:-}
MCP_PUBLIC_URL=${public_base_url}/mcp
MCP_OAUTH_ISSUER_URL=${public_base_url}
MCP_RESOURCE_METADATA_URL=${public_base_url}/.well-known/oauth-protected-resource
EOF
	sudo install -d -m 0750 -o root -g "$(id -gn)" "$(dirname "$ENV_FILE")"
	sudo install -m 0640 -o root -g "$(id -gn)" "$tmp_file" "$ENV_FILE"
	rm -f "$tmp_file"
}

wait_for_health() {
	local app_container health
	app_container="$(compose ps -q kaiten-mcp-http)"
	[[ -n "$app_container" ]] || fail "Could not find kaiten-mcp-http container."
	echo "Waiting for application health..."
	for _ in {1..60}; do
		health="$(docker_cmd inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$app_container")"
		if [[ "$health" == "healthy" ]]; then
			return 0
		fi
		sleep 2
	done
	fail "Application container did not become healthy; last status: $health."
}

extract_tunnel_url() {
	compose logs --no-color cloudflared 2>/dev/null \
		| sed -nE 's#.*(https://[-a-zA-Z0-9]+\.trycloudflare\.com).*#\1#p' \
		| tail -n 1
}

trap 'echo "ChatGPT tunnel deploy failed." >&2; show_debug >&2' ERR

[[ -d "$REPO_DIR/.git" ]] || fail "$REPO_DIR is not a git checkout."
if ! git -C "$REPO_DIR" diff --quiet || ! git -C "$REPO_DIR" diff --cached --quiet; then
	fail "$REPO_DIR has local changes. Commit, discard, or inspect them before deploying."
fi

if [[ -f "$BASE_ENV_FILE" ]]; then
	set -a
	# shellcheck disable=SC1090
	source "$BASE_ENV_FILE"
	set +a
fi

echo "Syncing $DEPLOY_REF from origin..."
git -C "$REPO_DIR" fetch --prune origin "$DEPLOY_REF"
if git -C "$REPO_DIR" show-ref --verify --quiet "refs/heads/$DEPLOY_REF"; then
	git -C "$REPO_DIR" checkout "$DEPLOY_REF"
else
	git -C "$REPO_DIR" checkout -b "$DEPLOY_REF" "origin/$DEPLOY_REF"
fi
git -C "$REPO_DIR" pull --ff-only origin "$DEPLOY_REF"

echo "Preparing placeholder OAuth env..."
write_tunnel_env "https://placeholder.invalid"

echo "Validating compose config..."
compose config --quiet

echo "Building and starting tunnel stack..."
compose build --pull kaiten-mcp-http
compose up -d --remove-orphans
wait_for_health

echo "Waiting for cloudflared quick tunnel URL..."
tunnel_url=""
for _ in {1..90}; do
	tunnel_url="$(extract_tunnel_url)"
	if [[ -n "$tunnel_url" ]]; then
		break
	fi
	sleep 2
done
[[ -n "$tunnel_url" ]] || fail "Could not find trycloudflare URL in cloudflared logs."
tunnel_url="${tunnel_url%/}"

echo "Configuring OAuth URLs for $tunnel_url..."
write_tunnel_env "$tunnel_url"
compose up -d --no-deps --force-recreate kaiten-mcp-http
wait_for_health

echo "Checking tunnel endpoints..."
curl -fsS --retry 12 --retry-delay 5 --retry-connrefused "$tunnel_url/healthz" >/dev/null
ready_json="$(curl -fsS --retry 12 --retry-delay 5 --retry-connrefused "$tunnel_url/readyz")"
echo "$ready_json" | grep -q '"auth_mode":"oauth"' || fail "/readyz did not report oauth auth mode: $ready_json"

metadata_json="$(curl -fsS "$tunnel_url/.well-known/oauth-protected-resource")"
echo "$metadata_json" | grep -q "\"resource\":\"$tunnel_url/mcp\"" || fail "OAuth metadata resource is wrong: $metadata_json"

mcp_status="$(curl -sS -o /tmp/kaiten-mcp-tunnel-unauth.json -w "%{http_code}" "$tunnel_url/mcp/")"
[[ "$mcp_status" == "401" ]] || fail "Unauthenticated /mcp/ returned HTTP $mcp_status instead of 401."

trap - ERR
echo "ChatGPT tunnel ready: $tunnel_url/mcp"
echo "Use this URL in ChatGPT Developer mode app settings."
