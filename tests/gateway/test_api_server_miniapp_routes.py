import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from gateway.config import PlatformConfig
from gateway.platforms.api_server import APIServerAdapter, cors_middleware, security_headers_middleware


BOT_TOKEN = "123456:telegram-token"


def _build_init_data(user_id: int = 12345) -> str:
    payload = {
        "auth_date": str(int(time.time())),
        "query_id": "AAEAAAE",
        "user": json.dumps({"id": user_id, "first_name": "Mini"}, separators=(",", ":")),
    }
    data_check_string = "\n".join(f"{key}={payload[key]}" for key in sorted(payload))
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    payload["hash"] = hmac.new(secret, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return urlencode(payload)


def _make_adapter() -> APIServerAdapter:
    return APIServerAdapter(
        PlatformConfig(
            enabled=True,
            extra={
                "key": "sk-secret",
                "telegram_miniapp_enabled": True,
                "telegram_bot_token": BOT_TOKEN,
                "telegram_allowed_users": ["12345"],
                "cors_origins": ["https://miniapp.example"],
            },
        )
    )


def _create_app(adapter: APIServerAdapter) -> web.Application:
    app = web.Application(middlewares=[mw for mw in (cors_middleware, security_headers_middleware) if mw is not None])
    app["api_server_adapter"] = adapter
    app.router.add_get("/health", adapter._handle_health)
    app.router.add_get("/v1/models", adapter._handle_models)
    app.router.add_get("/api/processes", adapter._handle_processes)
    app.router.add_get("/miniapp", adapter._handle_miniapp_index)
    app.router.add_get("/miniapp/", adapter._handle_miniapp_index)
    app.router.add_get("/miniapp/index.html", adapter._handle_miniapp_index)
    return app


@pytest.mark.asyncio
async def test_bearer_auth_still_authorizes_protected_routes():
    adapter = _make_adapter()
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get("/v1/models", headers={"Authorization": "Bearer sk-secret"})
        assert resp.status == 200
        data = await resp.json()
        assert data["object"] == "list"


@pytest.mark.asyncio
async def test_telegram_init_data_authorizes_protected_routes():
    adapter = _make_adapter()
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get("/v1/models", headers={"X-Telegram-Init-Data": _build_init_data()})
        assert resp.status == 200


@pytest.mark.asyncio
async def test_invalid_telegram_init_data_returns_stable_401_shape():
    adapter = _make_adapter()
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get("/v1/models", headers={"X-Telegram-Init-Data": "bad-data"})
        assert resp.status == 401
        data = await resp.json()
        assert data["error"]["type"] == "invalid_request_error"
        assert data["error"]["code"] in {"invalid_telegram_init_data", "invalid_telegram_signature"}


@pytest.mark.asyncio
async def test_cors_preflight_allows_miniapp_headers_without_overbroad_changes():
    adapter = _make_adapter()
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.options("/v1/models", headers={"Origin": "https://miniapp.example"})
        assert resp.status == 200
        allow_headers = resp.headers["Access-Control-Allow-Headers"]
        assert "X-Telegram-Init-Data" in allow_headers
        assert "X-Hermes-Session-Id" in allow_headers


@pytest.mark.asyncio
async def test_miniapp_static_routes_serve_html():
    adapter = _make_adapter()
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get("/miniapp/index.html")
        assert resp.status == 200
        assert resp.headers["Content-Type"].startswith("text/html")
        text = await resp.text()
        assert "Hermes Mini App (experimental)" in text


@pytest.mark.asyncio
async def test_processes_route_returns_process_list_shape():
    adapter = _make_adapter()
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get("/api/processes", headers={"Authorization": "Bearer sk-secret"})
        assert resp.status == 200
        data = await resp.json()
        assert "processes" in data
        assert isinstance(data["processes"], list)


@pytest.mark.asyncio
async def test_health_payload_includes_system_metrics_for_status_tab():
    adapter = _make_adapter()
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get("/health")
        assert resp.status == 200
        data = await resp.json()
        assert data["status"] == "ok"
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data
        assert "uptime" in data
