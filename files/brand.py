# -*- coding: utf-8 -*-
"""RoOtIt branding — do not edit. Integrity-checked at runtime."""
from __future__ import annotations

import hashlib
import sys

TITLE = "RoOtIt VPN IP LIMIT"
MEMORIAL = "1819 به یاد جاوید نامان"
SUPPORT = "https://t.me/AZROOT94"

_CANON = f"{TITLE}|{MEMORIAL}|{SUPPORT}"
_EXPECTED_SHA256 = "9a36c544bd4823ed5661071c0d871642c1e071ab26e16343d70db6a84450791b"


def header_line() -> str:
    return f"{TITLE} | {MEMORIAL}"


def wrap_message(body: str) -> str:
    body = (body or "").strip()
    h = header_line()
    if body.startswith(h):
        return body
    if body.startswith(TITLE):
        rest = body[len(TITLE) :].lstrip(" |\n")
        return f"{h}\n\n{rest}" if rest else h
    return f"{h}\n\n{body}" if body else h


def authorized_message() -> str:
    return wrap_message(f"دسترسی ادمین تأیید شد.\nپشتیبانی: {SUPPORT}")


def verify_integrity() -> None:
    got = hashlib.sha256(_CANON.encode("utf-8")).hexdigest()
    if got != _EXPECTED_SHA256:
        sys.stderr.write(
            "RoOtIt brand integrity check failed.\n"
            "Do not modify brand.py — reinstall from official source.\n"
        )
        sys.exit(2)
