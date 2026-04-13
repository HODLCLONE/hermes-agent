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
    app.router.add_get("/api/commands", adapter._handle_commands_index)
    app.router.add_post("/api/command", adapter._handle_command)
    return app


@pytest.mark.asyncio
async def test_get_commands_returns_structured_command_metadata(tmp_path):
    adapter = _make_adapter(tmp_path)
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.get("/api/commands", headers={"Authorization": "Bearer sk-secret"})
        assert resp.status == 200
        data = await resp.json()
        assert data["commands"]
        help_cmd = next(item for item in data["commands"] if item["name"] == "help")
        assert help_cmd["description"]
        assert "category" in help_cmd
        assert "aliases" in help_cmd


@pytest.mark.asyncio
async def test_post_command_executes_allowed_help_command(tmp_path):
    adapter = _make_adapter(tmp_path)
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.post(
            "/api/command",
            headers={"Authorization": "Bearer sk-secret", "X-Hermes-Session-Id": "sess-1"},
            json={"command": "/help"},
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["ok"] is True
        assert data["command"]["canonical"] == "help"
        assert data["session_id"] == "sess-1"
        assert "/help" in data["output"] or "/commands" in data["output"]


@pytest.mark.asyncio
async def test_post_command_rejects_invalid_command(tmp_path):
    adapter = _make_adapter(tmp_path)
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.post(
            "/api/command",
            headers={"Authorization": "Bearer sk-secret"},
            json={"command": "/definitely-not-real"},
        )
        assert resp.status == 400
        data = await resp.json()
        assert data["error"] == "Unknown or unsupported command"


@pytest.mark.asyncio
async def test_post_command_preserves_session_context_for_usage(tmp_path):
    adapter = _make_adapter(tmp_path)
    adapter._session_db.create_session("sess-usage", source="api_server", model="gpt-5.4")
    adapter._session_db.update_token_counts("sess-usage", input_tokens=50, output_tokens=20)
    app = _create_app(adapter)

    async with TestClient(TestServer(app)) as cli:
        resp = await cli.post(
            "/api/command",
            headers={"Authorization": "Bearer sk-secret", "X-Hermes-Session-Id": "sess-usage"},
            json={"command": "/usage"},
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["session_id"] == "sess-usage"
        assert "50" in data["output"]
        assert data["auth"]["mode"] == "bearer"
