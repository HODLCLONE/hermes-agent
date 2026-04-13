from unittest.mock import patch

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from gateway.config import PlatformConfig
from gateway.platforms.api_server import APIServerAdapter, cors_middleware
from hermes_state import SessionDB


def _make_adapter(tmp_path) -> APIServerAdapter:
    adapter = APIServerAdapter(PlatformConfig(enabled=True, extra={"key": "sk-secret"}))
    adapter._session_db = SessionDB(db_path=tmp_path / "state.db")
    return adapter


def _create_app(adapter: APIServerAdapter) -> web.Application:
    app = web.Application(middlewares=[cors_middleware])
    app["api_server_adapter"] = adapter
    app.router.add_get("/api/model-info", adapter._handle_model_info)
    app.router.add_get("/api/session-usage", adapter._handle_session_usage)
    return app


@pytest.mark.asyncio
async def test_model_info_returns_active_model_provider_and_context_length(tmp_path):
    adapter = _make_adapter(tmp_path)
    app = _create_app(adapter)

    with patch("gateway.platforms.api_server._resolve_gateway_model", return_value="gpt-5.4"), patch(
        "gateway.platforms.api_server._resolve_runtime_agent_kwargs",
        return_value={"provider": "openai", "base_url": "https://api.openai.com/v1"},
    ), patch("gateway.platforms.api_server.get_model_context_length", return_value=128000):
        async with TestClient(TestServer(app)) as cli:
            resp = await cli.get("/api/model-info", headers={"Authorization": "Bearer sk-secret"})
            assert resp.status == 200
            data = await resp.json()
            assert data["model"]["id"] == "gpt-5.4"
            assert data["model"]["provider"] == "openai"
            assert data["model"]["context_length"] == 128000


@pytest.mark.asyncio
async def test_session_usage_returns_zero_shape_when_session_missing(tmp_path):
    adapter = _make_adapter(tmp_path)
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get(
            "/api/session-usage",
            headers={"Authorization": "Bearer sk-secret", "X-Hermes-Session-Id": "missing-session"},
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["session_id"] == "missing-session"
        assert data["usage"]["input_tokens"] == 0
        assert data["usage"]["output_tokens"] == 0
        assert data["usage"]["total_tokens"] == 0
        assert data["usage"]["available"] is False


@pytest.mark.asyncio
async def test_session_usage_returns_cumulative_counts_for_current_session(tmp_path):
    adapter = _make_adapter(tmp_path)
    adapter._session_db.create_session("sess-1", source="api_server", model="gpt-5.4")
    adapter._session_db.update_token_counts("sess-1", input_tokens=120, output_tokens=30, cache_read_tokens=10)
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get(
            "/api/session-usage",
            headers={"Authorization": "Bearer sk-secret", "X-Hermes-Session-Id": "sess-1"},
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["usage"]["input_tokens"] == 120
        assert data["usage"]["output_tokens"] == 30
        assert data["usage"]["cache_read_tokens"] == 10
        assert data["usage"]["total_tokens"] == 160
        assert data["usage"]["available"] is True
