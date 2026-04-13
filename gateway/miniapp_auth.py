from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from typing import Any, Mapping
from urllib.parse import parse_qsl

_HEADER_NAME = "X-Telegram-Init-Data"
_MAX_INIT_DATA_AGE_SECONDS = 3600


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    mode: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    telegram_user_id: str | None = None
    display_name: str | None = None
    telegram_user: dict[str, Any] = field(default_factory=dict)


def _failure(code: str, message: str) -> AuthResult:
    return AuthResult(ok=False, error_code=code, error_message=message)


def extract_telegram_init_data(headers: Mapping[str, str] | None) -> str | None:
    if not headers:
        return None
    value = headers.get(_HEADER_NAME)
    if value is None:
        value = headers.get(_HEADER_NAME.lower())
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _parse_init_data(init_data: str) -> dict[str, str]:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
    if not parsed:
        raise ValueError("init data is empty")
    return parsed


def _build_data_check_string(values: Mapping[str, str]) -> str:
    parts = []
    for key in sorted(values):
        if key == "hash":
            continue
        parts.append(f"{key}={values[key]}")
    return "\n".join(parts)


def _display_name_from_user(user: Mapping[str, Any]) -> str | None:
    first = str(user.get("first_name") or "").strip()
    last = str(user.get("last_name") or "").strip()
    username = str(user.get("username") or "").strip()
    full = " ".join(part for part in (first, last) if part)
    if full:
        return full
    if username:
        return f"@{username}"
    return None


def validate_telegram_init_data(
    init_data: str,
    bot_token: str,
    allowed_user_ids: set[str] | None = None,
    *,
    max_age_seconds: int = _MAX_INIT_DATA_AGE_SECONDS,
) -> AuthResult:
    if not init_data:
        return _failure("missing_telegram_init_data", "Telegram Mini App auth requires X-Telegram-Init-Data.")
    if not bot_token:
        return _failure("telegram_bot_token_missing", "Telegram Mini App auth is not configured on this server.")

    try:
        parsed = _parse_init_data(init_data)
    except ValueError as exc:
        return _failure("invalid_telegram_init_data", f"Malformed Telegram init data: {exc}")

    provided_hash = parsed.get("hash", "").strip().lower()
    if not provided_hash:
        return _failure("invalid_telegram_signature", "Telegram init data is missing the hash field.")

    auth_date_raw = parsed.get("auth_date", "").strip()
    if not auth_date_raw:
        return _failure("invalid_telegram_init_data", "Telegram init data is missing auth_date.")
    try:
        auth_date = int(auth_date_raw)
    except ValueError:
        return _failure("invalid_telegram_init_data", "Telegram auth_date must be an integer timestamp.")

    now = int(time.time())
    if auth_date > now + 60:
        return _failure("telegram_auth_date_in_future", "Telegram init data auth_date is in the future.")
    if max_age_seconds > 0 and now - auth_date > max_age_seconds:
        return _failure("telegram_auth_expired", "Telegram init data has expired.")

    secret = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    data_check_string = _build_data_check_string(parsed)
    expected_hash = hmac.new(secret, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_hash, provided_hash):
        return _failure("invalid_telegram_signature", "Telegram init data signature check failed.")

    user_raw = parsed.get("user", "")
    if not user_raw:
        return _failure("invalid_telegram_init_data", "Telegram init data is missing the user payload.")
    try:
        user = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        return _failure("invalid_telegram_init_data", f"Telegram user payload is not valid JSON: {exc}")
    if not isinstance(user, dict):
        return _failure("invalid_telegram_init_data", "Telegram user payload must be an object.")

    telegram_user_id = str(user.get("id") or "").strip()
    if not telegram_user_id:
        return _failure("invalid_telegram_init_data", "Telegram user payload is missing id.")

    normalized_allowed = {str(user_id).strip() for user_id in (allowed_user_ids or set()) if str(user_id).strip()}
    if normalized_allowed and telegram_user_id not in normalized_allowed and "*" not in normalized_allowed:
        return _failure("telegram_user_not_allowed", "Telegram user is not allowed to use this Mini App.")

    return AuthResult(
        ok=True,
        mode="telegram_miniapp",
        telegram_user_id=telegram_user_id,
        display_name=_display_name_from_user(user),
        telegram_user=user,
    )


def resolve_miniapp_auth(
    headers: Mapping[str, str] | None,
    api_key: str,
    bot_token: str,
    owner_id: str | None,
    allowed_users: set[str] | None,
) -> AuthResult:
    auth_header = (headers or {}).get("Authorization", "") if headers else ""
    if api_key and auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token and hmac.compare_digest(token, api_key):
            return AuthResult(ok=True, mode="bearer")

    normalized_allowed = {str(user_id).strip() for user_id in (allowed_users or set()) if str(user_id).strip()}
    if owner_id:
        normalized_allowed.add(str(owner_id).strip())

    init_data = extract_telegram_init_data(headers)
    if init_data:
        return validate_telegram_init_data(init_data, bot_token, normalized_allowed)

    if api_key or bot_token:
        return _failure("missing_credentials", "Provide Authorization: Bearer <key> or X-Telegram-Init-Data.")
    return AuthResult(ok=True, mode="unauthenticated")
