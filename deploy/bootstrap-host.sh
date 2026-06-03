#!/usr/bin/env bash
set -Eeuo pipefail

APP_USER="${APP_USER:-mcpadmin}"
APP_GROUP="${APP_GROUP:-}"
APP_DIR="${APP_DIR:-/opt/kaiten-mcp/current}"
APP_PARENT="$(dirname "$APP_DIR")"
ENV_DIR="${ENV_DIR:-/etc/kaiten-mcp}"
ENV_FILE="${ENV_FILE:-$ENV_DIR/kaiten-mcp.env}"
REPO_URL="${REPO_URL:-https://github.com/ViktorOgnev/kaiten-mcp.git}"
DEPLOY_REF="${DEPLOY_REF:-remote-server-transport}"

run_root() {
	if [[ "${EUID}" -eq 0 ]]; then
		"$@"
	else
		sudo "$@"
	fi
}

run_app_user() {
	if [[ "${EUID}" -eq 0 ]]; then
		runuser -u "$APP_USER" -- "$@"
	else
		sudo -u "$APP_USER" "$@"
	fi
}

if ! id "$APP_USER" >/dev/null 2>&1; then
	echo "User '$APP_USER' does not exist. Create it first or set APP_USER." >&2
	exit 1
fi
if [[ -z "$APP_GROUP" ]]; then
	APP_GROUP="$(id -gn "$APP_USER")"
fi

echo "Installing host packages..."
run_root apt-get update
run_root env DEBIAN_FRONTEND=noninteractive apt-get install -y \
	ca-certificates \
	curl \
	docker-compose-v2 \
	docker.io \
	git

run_root systemctl enable --now docker
run_root usermod -aG docker "$APP_USER"

echo "Preparing directories..."
run_root install -d -m 0755 -o "$APP_USER" -g "$APP_GROUP" "$APP_PARENT"
run_root install -d -m 0750 -o root -g "$APP_GROUP" "$ENV_DIR"

if [[ ! -d "$APP_DIR/.git" ]]; then
	if [[ -e "$APP_DIR" && -n "$(find "$APP_DIR" -mindepth 1 -maxdepth 1 2>/dev/null)" ]]; then
		echo "$APP_DIR exists and is not a git checkout. Move it aside before bootstrapping." >&2
		exit 1
	fi
	run_root install -d -m 0755 -o "$APP_USER" -g "$APP_GROUP" "$APP_DIR"
	run_app_user git clone --branch "$DEPLOY_REF" "$REPO_URL" "$APP_DIR"
else
	run_app_user git -C "$APP_DIR" fetch --prune origin "$DEPLOY_REF"
fi

if [[ ! -f "$ENV_FILE" ]]; then
	echo "Creating $ENV_FILE from the public template..."
	run_root install -m 0640 -o root -g "$APP_GROUP" "$APP_DIR/deploy/.env.port.example" "$ENV_FILE"
fi

echo
echo "Bootstrap complete."
echo "Next:"
echo "  1. Open inbound TCP 8000 in the cloud firewall/security group."
echo "  2. Edit $ENV_FILE and set Kaiten credentials plus MCP_AUTH_TOKEN."
echo "  3. Run: $APP_DIR/deploy/deploy.sh"
echo
echo "If this is the current SSH session, docker group membership may require reconnecting."
