#!/usr/bin/env bash
# RoOtIt VPN IP LIMIT — uninstaller (clean remove for reinstall)
set -euo pipefail

TITLE="RoOtIt VPN IP LIMIT"
SUPPORT="https://t.me/AZROOT94"
PREFIX="/opt/vpn-ip-limit"
BIN_DIR="/usr/local/bin"
STATE_DIR="/var/lib/vpn-ip-limit"
CFG_DIR="/root/.pg_nodes"
PURGE_KEY=0

usage() {
  cat <<EOF
Usage: sudo bash uninstall.sh [--purge-key] [--yes]

  Removes RoOtIt VPN IP LIMIT services, binaries, config and logs.
  PasarGuard panel itself is NOT touched.

  --purge-key   also delete $CFG_DIR/api_key (use if key file is corrupted)
  --yes         do not ask confirmation

After uninstall, reinstall with:
  cd rootit-vpn-ip-limit
  sudo bash install.sh
  sudo vpn-ip-limit setup

Support: $SUPPORT
EOF
}

need_root() {
  if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
    echo "Run as root: sudo bash uninstall.sh"
    exit 1
  fi
}

YES=0
for arg in "$@"; do
  case "$arg" in
    -h|--help) usage; exit 0 ;;
    --purge-key) PURGE_KEY=1 ;;
    -y|--yes) YES=1 ;;
    *) echo "Unknown option: $arg"; usage; exit 1 ;;
  esac
done

need_root

echo "========================================"
echo "  $TITLE — UNINSTALL"
echo "  Support: $SUPPORT"
echo "========================================"
echo
echo "Will remove:"
echo "  - systemd: vpn-ip-limit.timer/service , vpn-ip-limit-bot.service"
echo "  - binaries: $BIN_DIR/vpn-ip-limit*"
echo "  - package:  $PREFIX"
echo "  - state:    $STATE_DIR"
echo "  - config:   $CFG_DIR/ip-limit.json , $CFG_DIR/panel_url"
echo "  - logs:     /var/log/vpn-ip-limit*.log , /tmp/vpn-ip-limit-diag.txt"
if [[ "$PURGE_KEY" -eq 1 ]]; then
  echo "  - API key:  $CFG_DIR/api_key  (--purge-key)"
else
  echo "  - API key:  KEEP (add --purge-key if file is corrupted)"
fi
echo
echo "Will NOT remove: PasarGuard panel, users, Xray, git clone folder."
echo

if [[ "$YES" -ne 1 ]]; then
  read -r -p "Continue uninstall? [yes/no]: " ans
  case "${ans,,}" in
    y|yes) ;;
    *) echo "Cancelled."; exit 0 ;;
  esac
fi

echo
echo "[1/5] Stopping services..."
systemctl stop vpn-ip-limit.timer vpn-ip-limit.service vpn-ip-limit-bot.service 2>/dev/null || true
systemctl disable vpn-ip-limit.timer vpn-ip-limit-bot.service 2>/dev/null || true

echo "[2/5] Removing systemd units..."
rm -f /etc/systemd/system/vpn-ip-limit.service \
      /etc/systemd/system/vpn-ip-limit.timer \
      /etc/systemd/system/vpn-ip-limit-bot.service
systemctl daemon-reload 2>/dev/null || true
systemctl reset-failed vpn-ip-limit.service vpn-ip-limit.timer vpn-ip-limit-bot.service 2>/dev/null || true

echo "[3/5] Removing binaries and package..."
rm -f "$BIN_DIR/vpn-ip-limit" \
      "$BIN_DIR/vpn-ip-limit-bot" \
      "$BIN_DIR/vpn-ip-limit-setup"
rm -rf "$PREFIX"

echo "[4/5] Removing state / config / logs..."
rm -rf "$STATE_DIR"
rm -f "$CFG_DIR/ip-limit.json" \
      "$CFG_DIR/panel_url" \
      /var/log/vpn-ip-limit.log \
      /var/log/vpn-ip-limit-bot.log \
      /tmp/vpn-ip-limit-diag.txt

if [[ "$PURGE_KEY" -eq 1 ]]; then
  if [[ -f "$CFG_DIR/api_key" ]]; then
    rm -f "$CFG_DIR/api_key"
    echo "      removed $CFG_DIR/api_key"
  fi
else
  # If key looks polluted (command text stuck to key), warn loudly
  if [[ -f "$CFG_DIR/api_key" ]]; then
    raw="$(tr -d '\r\n' < "$CFG_DIR/api_key")"
    if [[ "$raw" == *" "* || "$raw" == *sudo* || "$raw" == *setup* ]]; then
      echo
      echo "WARNING: $CFG_DIR/api_key looks corrupted:"
      echo "  $raw"
      echo "Re-run with:  sudo bash uninstall.sh --purge-key --yes"
      echo "Or fix now and reinstall will ask for a fresh key."
    fi
  fi
fi

echo "[5/5] Done."
echo
echo "========================================"
echo "  UNINSTALL COMPLETE"
echo "========================================"
echo "Reinstall:"
echo "  cd ~/rootit-vpn-ip-limit   # or your clone path"
echo "  git pull"
echo "  sudo bash install.sh"
echo "  sudo vpn-ip-limit setup"
echo
echo "If API key was bad, use:"
echo "  sudo bash uninstall.sh --purge-key --yes"
echo "  then install again and paste a CLEAN key from panel."
echo "Support: $SUPPORT"
