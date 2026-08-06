#!/usr/bin/env bash
# RoOtIt VPN IP LIMIT — portable installer
set -euo pipefail

TITLE="RoOtIt VPN IP LIMIT"
SUPPORT="https://t.me/AZROOT94"
PREFIX="/opt/vpn-ip-limit"
BIN_DIR="/usr/local/bin"
STATE_DIR="/var/lib/vpn-ip-limit"
CFG_DIR="/root/.pg_nodes"

need_root() {
  if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    echo "Run as root."
    exit 1
  fi
}

detect_api_key() {
  if [[ -f "$CFG_DIR/api_key" ]]; then
    echo "$CFG_DIR/api_key"
    return
  fi
  # common PasarGuard locations
  for p in /opt/pasarguard/.api_key /var/lib/pasarguard/api_key; do
    [[ -f "$p" ]] && echo "$p" && return
  done
  return 1
}

need_root
echo "========================================"
echo "  $TITLE installer"
echo "  Support: $SUPPORT"
echo "========================================"

if ! command -v python3 >/dev/null; then
  apt-get update -y && apt-get install -y python3
fi
if ! command -v systemctl >/dev/null; then
  echo "systemd is required."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$PREFIX" "$STATE_DIR" "$CFG_DIR" /var/log

# API key
if KEYFILE=$(detect_api_key); then
  if [[ "$KEYFILE" != "$CFG_DIR/api_key" ]]; then
    cp "$KEYFILE" "$CFG_DIR/api_key"
  fi
  echo "API key: $CFG_DIR/api_key"
else
  echo
  echo "PasarGuard API key not found."
  echo "Paste your panel API key (X-API-Key), then Enter:"
  read -r KEY
  if [[ -z "$KEY" ]]; then
    echo "API key required."
    exit 1
  fi
  printf '%s\n' "$KEY" > "$CFG_DIR/api_key"
  chmod 600 "$CFG_DIR/api_key"
fi

# Panel base URL (ask interactively unless PANEL_URL is already set)
ask_panel_url() {
  local current="http://127.0.0.1:8000"
  if [[ -f "$CFG_DIR/panel_url" ]]; then
    current="$(tr -d '\r\n' < "$CFG_DIR/panel_url")"
  fi
  if [[ -n "${PANEL_URL:-}" ]]; then
    echo "$PANEL_URL"
    return
  fi

  echo
  echo "PasarGuard panel address"
  echo "  Default is 127.0.0.1:8000"
  echo "  If your panel port is different, enter it below."
  echo
  local host port full
  read -r -p "Panel host [${current#http://}] (or full URL, Enter=keep): " full
  if [[ -z "$full" ]]; then
    echo "$current"
    return
  fi
  # If user typed only a port number
  if [[ "$full" =~ ^[0-9]+$ ]]; then
    echo "http://127.0.0.1:$full"
    return
  fi
  # If user typed host:port without scheme
  if [[ "$full" != http://* && "$full" != https://* ]]; then
    echo "http://$full"
    return
  fi
  echo "$full"
}

PANEL="$(ask_panel_url)"
PANEL="${PANEL%/}"
echo "Panel API: $PANEL"
printf '%s\n' "$PANEL" > "$CFG_DIR/panel_url"

# quick connectivity check
if command -v curl >/dev/null 2>&1; then
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 \
    -H "X-API-Key: $(cat "$CFG_DIR/api_key")" \
    "$PANEL/api/system" || true)"
  if [[ "$code" == "200" ]]; then
    echo "Panel check: OK ($code)"
  else
    echo "Panel check: WARNING http=$code (install continues; fix later with PANEL_URL or re-run install)"
  fi
fi

# copy package files
cp -a "$SCRIPT_DIR/files/core.py" "$PREFIX/core.py"
cp -a "$SCRIPT_DIR/files/fa_ui.py" "$PREFIX/fa_ui.py"
cp -a "$SCRIPT_DIR/files/vpn-ip-limit" "$BIN_DIR/vpn-ip-limit"
cp -a "$SCRIPT_DIR/files/vpn-ip-limit-bot" "$BIN_DIR/vpn-ip-limit-bot"
cp -a "$SCRIPT_DIR/files/vpn-ip-limit-setup" "$BIN_DIR/vpn-ip-limit-setup"
chmod +x "$BIN_DIR/vpn-ip-limit" "$BIN_DIR/vpn-ip-limit-bot" "$BIN_DIR/vpn-ip-limit-setup"

# default config (guard OFF)
if [[ ! -f "$CFG_DIR/ip-limit.json" ]]; then
  python3 - <<PY
import json, secrets
from pathlib import Path
cfg={
  "enabled": False,
  "default_limit": 2,
  "use_hwid_limit": True,
  "mode": "disable",
  "punish_seconds": 45,
  "cooldown_seconds": 180,
  "exempt_usernames": [],
  "log_file": "/var/log/vpn-ip-limit.log",
  "telegram": {
    "enabled": True,
    "bot_token": "",
    "bot_username": "",
    "bot_id": "",
    "admin_ids": [],
    "access_password": secrets.token_urlsafe(6),
    "support": "$SUPPORT",
    "chat_id": ""
  }
}
Path("$CFG_DIR/ip-limit.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print("created config")
PY
fi

# systemd units
cat > /etc/systemd/system/vpn-ip-limit.service <<'EOF'
[Unit]
Description=VPN concurrent IP limit (PasarGuard)
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/vpn-ip-limit run
Nice=10
EOF

cat > /etc/systemd/system/vpn-ip-limit.timer <<'EOF'
[Unit]
Description=Run VPN IP limit every 20s

[Timer]
OnBootSec=30
OnUnitActiveSec=20
AccuracySec=5
Unit=vpn-ip-limit.service

[Install]
WantedBy=timers.target
EOF

cat > /etc/systemd/system/vpn-ip-limit-bot.service <<'EOF'
[Unit]
Description=RoOtIt VPN IP LIMIT Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/vpn-ip-limit-bot
Restart=always
RestartSec=3
Nice=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
# ensure IP guard is NOT started by installer
systemctl stop vpn-ip-limit.timer vpn-ip-limit.service 2>/dev/null || true
systemctl disable vpn-ip-limit.timer 2>/dev/null || true

# bot service: enable and restart so updates apply; keep IP guard off
systemctl enable vpn-ip-limit-bot.service >/dev/null 2>&1 || true
systemctl restart vpn-ip-limit-bot.service >/dev/null 2>&1 || true

# panel_url helper already supported inside core.py v1.1+
if [[ ! -f "$CFG_DIR/panel_url" ]]; then
  printf '%s\n' "$PANEL" > "$CFG_DIR/panel_url"
fi

echo
echo "Install/Update OK. version files copied."
echo "Next (first install only): vpn-ip-limit setup"
echo "Diagnostics: vpn-ip-limit diag"
echo "Bot log:     /var/log/vpn-ip-limit-bot.log"
echo
echo "IP Guard stays OFF until you start it from Telegram menu."
echo "Support: $SUPPORT"