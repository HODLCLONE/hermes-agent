"""Tests for /app gateway slash command."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from gateway.config import GatewayConfig, Platform, PlatformConfig
from gateway.hooks import HookRegistry
from gateway.platforms.base import MessageEvent
from gateway.session import SessionSource


def _make_event(text="/app", platform=Platform.TELEGRAM, user_id="12345", chat_id="67890"):
    source = SessionSource(
        platform=platform,
        user_id=user_id,
        chat_id=chat_id,
        user_name="testuser",
    )
    return MessageEvent(text=text, source=source)


def _make_runner(*, telegram_extra=None, api_server_extra=None):
    from gateway.run import GatewayRunner

    runner = object.__new__(GatewayRunner)
    runner.config = GatewayConfig(
        platforms={
            Platform.TELEGRAM: PlatformConfig(enabled=True, token="test-token", extra=telegram_extra or {}),
            Platform.API_SERVER: PlatformConfig(enabled=True, token="", extra=api_server_extra or {}),
        }
    )
    runner.adapters = {}
    runner._voice_mode = {}
    runner.hooks = HookRegistry()
    runner.session_store = MagicMock()
    runner._session_db = None
    return runner


class TestAppCommand:
    @pytest.mark.asyncio
    async def test_help_output_includes_app(self):
        runner = _make_runner()
        result = await runner._handle_help_command(_make_event(text="/help"))
        assert "/app" in result

    @pytest.mark.asyncio
    async def test_app_command_sends_telegram_launcher_button(self):
        runner = _make_runner(telegram_extra={"miniapp_url": "https://example.com/miniapp/"})
        adapter = SimpleNamespace(send_miniapp_launcher=AsyncMock(return_value=SimpleNamespace(success=True)))
        runner.adapters = {Platform.TELEGRAM: adapter}

        result = await runner._handle_app_command(_make_event())

        assert result is None
        adapter.send_miniapp_launcher.assert_awaited_once_with(
            chat_id="67890",
            url="https://example.com/miniapp/",
            reply_to=None,
            metadata=None,
        )

    @pytest.mark.asyncio
    async def test_app_command_falls_back_to_configured_api_server_public_url(self):
        runner = _make_runner(api_server_extra={"public_url": "https://example.com"})
        adapter = SimpleNamespace(send_miniapp_launcher=AsyncMock(return_value=SimpleNamespace(success=True)))
        runner.adapters = {Platform.TELEGRAM: adapter}

        await runner._handle_app_command(_make_event())

        adapter.send_miniapp_launcher.assert_awaited_once_with(
            chat_id="67890",
            url="https://example.com/miniapp/",
            reply_to=None,
            metadata=None,
        )

    @pytest.mark.asyncio
    async def test_app_command_rejects_non_telegram_platforms(self):
        runner = _make_runner(telegram_extra={"miniapp_url": "https://example.com/miniapp/"})
        adapter = SimpleNamespace(send_miniapp_launcher=AsyncMock(return_value=SimpleNamespace(success=True)))
        runner.adapters = {Platform.TELEGRAM: adapter}

        result = await runner._handle_app_command(_make_event(platform=Platform.DISCORD))

        assert "only available on telegram" in result.lower()
        adapter.send_miniapp_launcher.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_app_command_reports_missing_url(self):
        runner = _make_runner()

        result = await runner._handle_app_command(_make_event())

        assert "not configured" in result.lower()
        assert "mini app" in result.lower()
