#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

KEY_PATH = Path("/root/.pg_nodes/api_key")
CFG_PATH = Path("/root/.pg_nodes/ip-limit.json")
STATE_PATH = Path("/var/lib/vpn-ip-limit/state.json")
BASE = "http://127.0.0.1:8000"
SUPPORT = "https://t.me/AZROOT94"
TITLE = "RoOtIt VPN IP LIMIT"


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_cfg() -> dict:
    cfg = load_json(CFG_PATH, {})
    cfg.setdefault("enabled", False)
    cfg.setdefault("default_limit", 2)
    cfg.setdefault("use_hwid_limit", True)
    cfg.setdefault("mode", "disable")
    cfg.setdefault("punish_seconds", 45)
    cfg.setdefault("cooldown_seconds", 180)
    cfg.setdefault("exempt_usernames", [])
    cfg.setdefault("log_file", "/var/log/vpn-ip-limit.log")
    tg = cfg.setdefault("telegram", {})
    tg.setdefault("enabled", True)
    tg.setdefault("bot_token", "")
    tg.setdefault("bot_username", "mamerootitbot")
    tg.setdefault("chat_id", "")
    tg.setdefault("access_password", "")
    tg.setdefault("admin_ids", [])  # telegram numeric user ids allowed without password
    tg.setdefault("bot_username", "")
    tg.setdefault("support", SUPPORT)
    return cfg


def save_cfg(cfg: dict) -> None:
    save_json(CFG_PATH, cfg)


def load_state() -> dict:
    return load_json(STATE_PATH, {})


def save_state(state: dict) -> None:
    save_json(STATE_PATH, state)


def get_key() -> str:
    return KEY_PATH.read_text(encoding="utf-8").strip()


def log(msg: str, cfg: dict | None = None) -> None:
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z {msg}"
    print(line, flush=True)
    path = (cfg or {}).get("log_file") if cfg else "/var/log/vpn-ip-limit.log"
    try:
        with open(path or "/var/log/vpn-ip-limit.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def api(method: str, path: str, body: dict | None = None, key: str = ""):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"X-API-Key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return json.loads(raw) if raw else {}


def collect_ips(nodes_blob: dict) -> dict[str, int]:
    merged: dict[str, int] = {}
    for node_data in ((nodes_blob or {}).get("nodes") or {}).values():
        if not node_data:
            continue
        for ip, ts in (node_data.get("ips") or {}).items():
            if ip in ("127.0.0.1", "::1"):
                continue
            try:
                tsi = int(ts)
            except Exception:
                tsi = 0
            if tsi >= merged.get(ip, 0):
                merged[ip] = tsi
    return merged


def user_limit(user: dict, cfg: dict) -> int:
    if cfg.get("use_hwid_limit") and user.get("hwid_limit") is not None:
        lim = int(user["hwid_limit"])
        return 0 if lim == 0 else lim
    return int(cfg.get("default_limit", 2))


def list_users(key: str) -> list:
    return api("GET", "/api/users?offset=0&limit=500", key=key).get("users", [])


def set_user_fields(key: str, username: str, fields: dict) -> dict:
    return api("PUT", f"/api/user/{username}", fields, key)


def timer_active() -> bool:
    return os.system("systemctl is-active --quiet vpn-ip-limit.timer") == 0


def service_enable() -> None:
    os.system("systemctl enable --now vpn-ip-limit.timer >/dev/null 2>&1")


def service_disable() -> None:
    os.system("systemctl stop vpn-ip-limit.timer vpn-ip-limit.service >/dev/null 2>&1")
    os.system("systemctl disable vpn-ip-limit.timer >/dev/null 2>&1")


def authorized_chats(state: dict) -> list[str]:
    return [str(x) for x in (state.get("authorized_chats") or [])]


def add_authorized_chat(state: dict, chat_id) -> None:
    chats = state.setdefault("authorized_chats", [])
    s = str(chat_id)
    if s not in chats:
        chats.append(s)


def notify_all(cfg: dict, state: dict, text: str) -> None:
    tg = cfg.get("telegram") or {}
    if not tg.get("enabled"):
        return
    token = (tg.get("bot_token") or "").strip()
    if not token:
        return
    targets = set(authorized_chats(state))
    legacy = str(tg.get("chat_id") or "").strip()
    if legacy:
        targets.add(legacy)
    for chat_id in targets:
        try:
            tg_api(token, "sendMessage", {
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            })
        except Exception as e:
            log(f"TG_ERR chat={chat_id} {e}", cfg)


def tg_api(token: str, method: str, payload: dict):
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def status_report(cfg: dict, key: str) -> str:
    lines = [
        f"{TITLE}",
        f"IP Guard: {'ON' if cfg.get('enabled') else 'OFF'} | Timer: {'ON' if timer_active() else 'OFF'} | Mode: {cfg.get('mode')}",
        f"Default IP limit: {cfg.get('default_limit')}",
        f"Exempt users: {', '.join(cfg.get('exempt_usernames') or []) or '-'}",
        "",
        f"{'FLAG':<5} {'USER':<14} {'STATUS':<8} {'LIM':<4} {'N':<3} IPS",
    ]
    for u in list_users(key):
        lim = user_limit(u, cfg)
        lim_s = "INF" if lim <= 0 else str(lim)
        try:
            blob = api("GET", f"/api/node/online_stats/{u['id']}/ip", key=key)
            ips = collect_ips(blob)
        except Exception:
            lines.append(f"ERR   {u['username']:<14} error")
            continue
        flag = "OVER" if (lim > 0 and len(ips) > lim) else "OK"
        ip_s = ",".join(ips.keys()) if ips else "-"
        if len(ip_s) > 40:
            ip_s = ip_s[:37] + "..."
        lines.append(f"{flag:<5} {u['username']:<14} {u.get('status',''):<8} {lim_s:<4} {len(ips):<3} {ip_s}")
    return "\n".join(lines)


def run_once(cfg: dict, state: dict, key: str) -> list[str]:
    """Enforce limits. Returns list of action messages."""
    actions = []
    if not cfg.get("enabled", False):
        return actions

    users = list_users(key)
    exempt = set(cfg.get("exempt_usernames") or [])
    now = time.time()
    mode = cfg.get("mode", "disable")
    last = state.setdefault("last_action", {})
    punished = state.setdefault("punished", {})

    # kick-mode restore
    if mode == "kick":
        done = []
        for username, meta in list(punished.items()):
            if now < float(meta.get("until", 0)):
                continue
            try:
                u = api("GET", f"/api/user/{username}", key=key)
                if u.get("status") == "disabled" and meta.get("by") == "vpn-ip-limit":
                    set_user_fields(key, username, {"status": "active"})
                    msg = f"RESTORE {username}"
                    log(msg, cfg)
                    actions.append(msg)
                done.append(username)
            except Exception as e:
                log(f"RESTORE_ERR {username}: {e}", cfg)
        for username in done:
            punished.pop(username, None)

    for u in users:
        username = u.get("username")
        uid = u.get("id")
        if not username or uid is None or username in exempt or u.get("status") != "active":
            continue
        if mode == "kick" and username in punished:
            continue
        lim = user_limit(u, cfg)
        if lim <= 0:
            continue
        try:
            blob = api("GET", f"/api/node/online_stats/{uid}/ip", key=key)
        except Exception as e:
            log(f"IP_ERR {username}: {e}", cfg)
            continue
        ips = collect_ips(blob)
        if len(ips) <= lim:
            continue

        ranked = sorted(ips.items(), key=lambda x: x[1], reverse=True)
        excess = [ip for ip, _ in ranked[lim:]]
        cooldown = float(cfg.get("cooldown_seconds", 180))
        prev = float(last.get(username, 0) or 0)
        if mode == "kick" and now - prev < cooldown:
            continue

        set_user_fields(key, username, {"status": "disabled"})
        last[username] = now
        state.setdefault("disabled_by_script", {})[username] = {
            "at": now, "ips": list(ips), "limit": lim, "by": "vpn-ip-limit"
        }
        if mode == "kick":
            punished[username] = {
                "until": now + float(cfg.get("punish_seconds", 45)),
                "by": "vpn-ip-limit",
                "ips": list(ips),
                "excess": excess,
            }
        else:
            punished.pop(username, None)

        msg = f"DISABLED {username} limit={lim} ips={list(ips.keys())} excess={excess} mode={mode}"
        log(f"VIOLATION/ACTION {msg}", cfg)
        actions.append(msg)
        notify_all(
            cfg,
            state,
            "\n".join(
                [
                    f"[{TITLE}]",
                    f"User: {username}",
                    f"Action: DISABLED ({'until manual enable' if mode=='disable' else 'kick temporary'})",
                    f"Limit: {lim}",
                    f"IPs: {', '.join(ips.keys())}",
                    f"Excess: {', '.join(excess)}",
                    f"Support: {SUPPORT}",
                ]
            ),
        )
    return actions


def tail_log(cfg: dict, n: int = 20) -> str:
    path = Path(cfg.get("log_file") or "/var/log/vpn-ip-limit.log")
    if not path.exists():
        return "No log yet."
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-n:]) or "Log empty."
