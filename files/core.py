#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import brand as B

B.verify_integrity()

KEY_PATH = Path("/root/.pg_nodes/api_key")
CFG_PATH = Path("/root/.pg_nodes/ip-limit.json")
STATE_PATH = Path("/var/lib/vpn-ip-limit/state.json")
PANEL_URL_PATH = Path("/root/.pg_nodes/panel_url")
BOT_LOG_PATH = Path("/var/log/vpn-ip-limit-bot.log")
SUPPORT = B.SUPPORT
TITLE = B.TITLE
VERSION = "1.1.3"


def _sanitize_panel_url(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        return "http://127.0.0.1:8000"
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith(("http://", "https://")):
            return line.rstrip("/")
    if re.fullmatch(r"\d+", raw):
        return f"http://127.0.0.1:{raw}"
    if re.fullmatch(r"[\w.-]+:\d+", raw):
        return f"http://{raw.rstrip('/')}"
    return "http://127.0.0.1:8000"


def _panel_base() -> str:
    if not PANEL_URL_PATH.exists():
        return "http://127.0.0.1:8000"
    stored = PANEL_URL_PATH.read_text(encoding="utf-8")
    url = _sanitize_panel_url(stored)
    if stored.strip() != url:
        try:
            PANEL_URL_PATH.write_text(url + "\n", encoding="utf-8")
        except OSError:
            pass
    return url


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
    raw = KEY_PATH.read_text(encoding="utf-8").strip()
    # recover if file was polluted (e.g. "sudo vpn-ip-limit setuppg_key_...")
    m = re.search(r"(pg_key_[0-9a-fA-F-]+|[0-9a-fA-F]{8,}(?:-[0-9a-fA-F]+)*)", raw)
    if m:
        key = m.group(1)
        if key != raw:
            try:
                KEY_PATH.write_text(key + "\n", encoding="utf-8")
                KEY_PATH.chmod(0o600)
            except OSError:
                pass
        return key
    # last token if junk was prepended on same line
    parts = raw.split()
    if parts:
        return parts[-1]
    raise RuntimeError(f"empty API key in {KEY_PATH}")


def _ssl_context_for(url: str):
    if not url.lower().startswith("https://"):
        return None
    import ssl

    # Local/panel HTTPS often has cert for domain, not 127.0.0.1 — skip verify.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def log(msg: str, cfg: dict | None = None) -> None:
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z {msg}"
    print(line, flush=True)
    path = (cfg or {}).get("log_file") if cfg else "/var/log/vpn-ip-limit.log"
    try:
        with open(path or "/var/log/vpn-ip-limit.log", "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def blog(msg: str) -> None:
    """Bot log for Telegram menu debugging. Ask users to send this file."""
    line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}Z {msg}"
    print(line, flush=True)
    try:
        BOT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(BOT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def tail_file(path: Path | str, n: int = 40) -> str:
    path = Path(path)
    if not path.exists():
        return f"(missing) {path}"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:]) if lines else "(empty)"
    except Exception as e:
        return f"(read error) {e}"


def panel_ping(key: str) -> tuple[bool, str, str]:
    """Returns (ok, url, short_error_or_empty)."""
    base = _panel_base()
    try:
        api("GET", "/api/system", key=key)
        return True, base, ""
    except Exception as e:
        return False, base, str(e).strip() or type(e).__name__


def _panel_hint(url: str, err: str) -> list[str]:
    err_l = (err or "").lower()
    hints = [
        "احتمال‌ها و کارهایی که باید چک کنید:",
        f"• آدرس فعلی پنل: {url}",
        "• اگر پنل HTTPS است، آدرس باید با https:// شروع شود",
        "• پورت را درست وارد کنید (مثلاً 8000 نه 2087 مگر واقعاً همان باشد)",
        "• API Key پنل را دوباره در /root/.pg_nodes/api_key بررسی کنید",
        "• روی سرور تست کنید:",
        f"  curl -sS -o /dev/null -w '%{{http_code}}' -H \"X-API-Key: $(cat /root/.pg_nodes/api_key)\" {url}/api/system",
        "• بعد از اصلاح:",
        "  echo 'http://127.0.0.1:PORT' > /root/.pg_nodes/panel_url",
        "  systemctl restart vpn-ip-limit-bot",
    ]
    if "ssl" in err_l or "certificate" in err_l:
        hints.insert(1, "• خطای SSL: احتمالاً باید http را به https عوض کنید (یا برعکس)")
    if "refused" in err_l:
        hints.insert(1, "• اتصال رد شد: پنل روی این پورت روشن نیست")
    if "closed connection" in err_l or "remotedisconnected" in err_l:
        hints.insert(1, "• اتصال قطع شد: اغلب پورت/پروتکل اشتباه است (http روی پورت https یا برعکس)")
    if "unknown url type" in err_l or "illegal" in err_l:
        hints.insert(1, "• آدرس پنل خراب است؛ فایل panel_url را اصلاح کنید")
    return hints


def _short_errors(text: str, max_lines: int = 8) -> list[str]:
    lines = [ln.rstrip() for ln in (text or "").splitlines() if ln.strip()]
    errs = [ln for ln in lines if any(k in ln for k in ("ERR", "Error", "Traceback", "FAIL", "CB_ERR", "Exception", "RemoteDisconnected", "URLError"))]
    if not errs:
        errs = lines[-max_lines:]
    return errs[-max_lines:]


def diagnostics_report(cfg: dict, key: str) -> str:
    import subprocess

    state = load_state()
    tg = cfg.get("telegram") or {}
    panel_ok, panel_url, panel_err = panel_ping(key)
    key_ok = KEY_PATH.exists()
    cfg_ok = CFG_PATH.exists()
    guard_on = bool(cfg.get("enabled"))
    timer_on = timer_active()
    try:
        bot_svc = subprocess.check_output(
            ["systemctl", "is-active", "vpn-ip-limit-bot.service"],
            stderr=subprocess.STDOUT,
            text=True,
            timeout=5,
        ).strip()
    except Exception as e:
        bot_svc = f"error ({e})"
    bot_ok = bot_svc == "active"
    token_ok = bool((tg.get("bot_token") or "").strip())

    status_ok = False
    status_note = ""
    if panel_ok:
        try:
            status_report(cfg, key)
            status_ok = True
            status_note = "خواندن لیست کاربران و IPها موفق بود"
        except Exception as e:
            status_note = str(e).strip() or type(e).__name__
    else:
        status_note = "به‌خاطر قطع بودن پنل قابل تست نیست"

    problems = []
    if not panel_ok:
        problems.append("اتصال به پنل PasarGuard برقرار نیست")
    if not key_ok:
        problems.append("فایل API Key پیدا نشد")
    if not cfg_ok:
        problems.append("فایل تنظیمات پیدا نشد")
    if not bot_ok:
        problems.append(f"سرویس ربات فعال نیست ({bot_svc})")
    if not token_ok:
        problems.append("توکن ربات تنظیم نشده")
    if panel_ok and not status_ok:
        problems.append("خواندن وضعیت کاربران از پنل شکست خورد")

    if not problems:
        summary = "✅ همه چیز ظاهراً سالم است"
    elif len(problems) == 1 and not panel_ok:
        summary = "❌ مشکل اصلی: پنل در دسترس نیست"
    else:
        summary = f"❌ {len(problems)} مورد نیاز به بررسی دارد"

    mode = cfg.get("mode") or "disable"
    mode_fa = "قطع کامل تا فعال‌سازی دستی" if mode == "disable" else f"موقت ({mode})"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"گزارش عیب‌یابی v{VERSION}",
        f"زمان: {now}",
        "",
        "—— خلاصه ——",
        summary,
    ]
    for p in problems:
        lines.append(f"• {p}")

    lines += [
        "",
        "—— وضعیت ——",
        f"پنل:           {'✅ وصل' if panel_ok else '❌ قطع'}",
        f"آدرس پنل:      {panel_url}",
        f"API Key:       {'✅ هست' if key_ok else '❌ نیست'}",
        f"تنظیمات:       {'✅ هست' if cfg_ok else '❌ نیست'}",
        f"ربات تلگرام:   {'✅ فعال' if bot_ok else '❌ ' + bot_svc}",
        f"توکن ربات:     {'✅ تنظیم شده' if token_ok else '❌ خالی'}",
        f"محافظ IP:      {'🟢 روشن' if guard_on else '⚪ خاموش'}",
        f"تایمر بررسی:   {'🟢 روشن' if timer_on else '⚪ خاموش'}",
        f"حالت تنبیه:    {mode_fa}",
        f"حد پیش‌فرض IP: {cfg.get('default_limit')}",
        f"ربات:          @{tg.get('bot_username') or '-'}",
        f"ادمین‌ها:      {tg.get('admin_ids') or []}",
        f"نشست فعال:     {authorized_chats(state)}",
        f"تست کاربران:   {'✅ ' + status_note if status_ok else '❌ ' + status_note}",
    ]

    if not panel_ok:
        lines += ["", "—— راهنمای رفع مشکل پنل ——"]
        lines += _panel_hint(panel_url, panel_err)
        if panel_err:
            lines += ["", f"خطای کوتاه: {panel_err[:300]}"]

    # compact recent errors (no huge traceback dump in Telegram)
    bot_tail = tail_file(BOT_LOG_PATH, 80)
    act_path = cfg.get("log_file") or "/var/log/vpn-ip-limit.log"
    act_tail = tail_file(act_path, 40)
    short = _short_errors(bot_tail, 6)
    if short:
        lines += ["", "—— آخرین خطاهای ربات (کوتاه) ——"]
        lines.extend(short)

    act_lines = [ln for ln in act_tail.splitlines() if ln.strip() and not ln.startswith("(missing)")]
    if act_lines:
        lines += ["", "—— آخرین عملیات محافظ (حداکثر ۱۰ خط) ——"]
        lines.extend(act_lines[-10:])
    elif "(missing)" in act_tail:
        lines += ["", "—— لاگ عملیات ——", "هنوز فایلی ساخته نشده (محافظ هنوز عملی انجام نداده)"]

    lines += [
        "",
        "—— فایل‌های سرور ——",
        "/tmp/vpn-ip-limit-diag.txt",
        "/var/log/vpn-ip-limit-bot.log",
        str(act_path),
        f"پشتیبانی: {SUPPORT}",
    ]

    text = "\n".join(lines)
    # full technical dump only on disk for support
    full = "\n".join(
        [
            text,
            "",
            "======== RAW (for support) ========",
            f"panel_ok={panel_ok} url={panel_url} err={panel_err}",
            f"bot_service={bot_svc}",
            "",
            "--- bot log last 40 ---",
            "\n".join(bot_tail.splitlines()[-40:]),
            "",
            "--- action log last 30 ---",
            "\n".join(act_tail.splitlines()[-30:]),
        ]
    )
    try:
        Path("/tmp/vpn-ip-limit-diag.txt").write_text(full, encoding="utf-8")
    except OSError:
        pass
    return text


def api(method: str, path: str, body: dict | None = None, key: str = ""):
    data = None if body is None else json.dumps(body).encode()
    url = _panel_base() + path
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"X-API-Key": key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30, context=_ssl_context_for(url)) as r:
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
