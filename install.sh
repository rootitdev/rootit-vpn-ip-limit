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

# Panel base URL for local API
PANEL="${PANEL_URL:-http://127.0.0.1:8000}"
echo "Panel API: $PANEL"
# write panel url helper for core
printf '%s\n' "$PANEL" > "$CFG_DIR/panel_url"

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

# patch core to honor panel_url if present
python3 - <<'PY'
from pathlib import Path
p=Path('/opt/vpn-ip-limit/core.py')
t=p.read_text(encoding='utf-8')
if 'panel_url' not in t:
    old='BASE = "http://127.0.0.1:8000"'
    new='''def _panel_base():
    p = Path("/root/.pg_nodes/panel_url")
    if p.exists():
        v = p.read_text(encoding="utf-8").strip()
        if v:
            return v.rstrip("/")
    return "http://127.0.0.1:8000"

BASE = _panel_base()'''
    if old not in t:
        raise SystemExit('BASE marker missing')
    p.write_text(t.replace(old,new,1), encoding='utf-8')
    print('panel_url support added')
else:
    print('panel_url already present')
PY

echo
echo "Install OK."
echo "Next: configure Telegram bot"
echo "  vpn-ip-limit setup"
echo
echo "IP Guard stays OFF until you start it from Telegram menu."
echo "Support: $SUPPORT"