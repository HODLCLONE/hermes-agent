#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import logging
import os
import signal
from pathlib import Path

from dotenv import load_dotenv

from gateway.config import GatewayConfig, Platform, PlatformConfig, load_gateway_config
from gateway.platforms.api_server import APIServerAdapter
from hermes_cli.config import get_hermes_home


def _load_env() -> None:
    hermes_home = get_hermes_home()
    env_path = hermes_home / '.env'
    if env_path.exists():
        try:
            load_dotenv(env_path, override=True, encoding='utf-8')
        except UnicodeDecodeError:
            load_dotenv(env_path, override=True, encoding='latin-1')


def _adapter_from_config() -> APIServerAdapter:
    cfg: GatewayConfig = load_gateway_config()
    platform_cfg = cfg.platforms.get(Platform.API_SERVER)
    if platform_cfg is None:
        platform_cfg = PlatformConfig(enabled=True, extra={})
    platform_cfg.enabled = True
    platform_cfg.extra = dict(platform_cfg.extra or {})
    platform_cfg.extra.setdefault('host', os.getenv('API_SERVER_HOST', '127.0.0.1'))
    platform_cfg.extra.setdefault('port', int(os.getenv('API_SERVER_PORT', '8765')))
    platform_cfg.extra.setdefault('telegram_miniapp_enabled', True)
    platform_cfg.extra.setdefault('cors_origins', ['*'])
    if not platform_cfg.extra.get('key') and os.getenv('API_SERVER_KEY'):
        platform_cfg.extra['key'] = os.getenv('API_SERVER_KEY')
    return APIServerAdapter(platform_cfg)


async def main() -> int:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    _load_env()
    adapter = _adapter_from_config()
    ok = await adapter.connect()
    if not ok:
        return 1

    public_path = f"http://{adapter._host}:{adapter._port}/miniapp/"
    print(f'Miniapp API server running at {public_path}', flush=True)

    stop_event = asyncio.Event()

    def _request_stop(*_args):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_stop)
        except NotImplementedError:
            pass

    await stop_event.wait()
    await adapter.disconnect()
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
