import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

from gateway.miniapp_auth import (
    extract_telegram_init_data,
    resolve_miniapp_auth,
    validate_telegram_init_data,
)


BOT_TOKEN = "123456:telegram-token"


def _build_init_data(*, user_id: int = 12345, first_name: str = "Mini", auth_date: int | None = None, extra: dict | None = None) -> str:
    auth_date = auth_date or int(time.time())
    payload = {
        "auth_date": str(auth_date),
        "query_id": "AAEAAAE",
        "user": json.dumps({"id": user_id, "first_name": first_name, "username": "miniapp"}, separators=(",", ":")),
    }
    if extra:
        payload.update(extra)
    data_check_string = "\n".join(
        f"{key}={payload[key]}" for key in sorted(payload)
    )
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    payload["hash"] = hmac.new(secret, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return urlencode(payload)


def test_extract_telegram_init_data_returns_none_when_missing():
    assert extract_telegram_init_data({}) is None


def test_validate_telegram_init_data_fails_cleanly_for_malformed_payload():
    result = validate_telegram_init_data("not=query&%ZZ", BOT_TOKEN, {"12345"})

    assert result.ok is False
    assert result.error_code == "invalid_telegram_init_data"


def test_validate_telegram_init_data_accepts_allowed_user():
    init_data = _build_init_data(user_id=12345, first_name="Hermes")

    result = validate_telegram_init_data(init_data, BOT_TOKEN, {"12345"})

    assert result.ok is True
    assert result.mode == "telegram_miniapp"
    assert result.telegram_user_id == "12345"
    assert result.display_name == "Hermes"


def test_validate_telegram_init_data_rejects_unauthorized_user():
    init_data = _build_init_data(user_id=99999)

    result = validate_telegram_init_data(init_data, BOT_TOKEN, {"12345"})

    assert result.ok is False
    assert result.error_code == "telegram_user_not_allowed"


def test_resolve_miniapp_auth_keeps_bearer_fallback_independent():
    result = resolve_miniapp_auth(
        {"Authorization": "Bearer sk-test"},
        api_key="sk-test",
        bot_token=BOT_TOKEN,
        owner_id=None,
        allowed_users={"12345"},
    )

    assert result.ok is True
    assert result.mode == "bearer"


def test_resolve_miniapp_auth_requires_header_when_telegram_auth_is_used():
    result = resolve_miniapp_auth({}, api_key="", bot_token=BOT_TOKEN, owner_id="12345", allowed_users=set())

    assert result.ok is False
    assert result.error_code == "missing_credentials"
