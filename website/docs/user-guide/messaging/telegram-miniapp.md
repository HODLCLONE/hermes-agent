---
sidebar_position: 2
title: "Telegram Mini App"
description: "Enable the experimental Hermes Telegram Mini App"
---

# Telegram Mini App

Hermes includes an **experimental, optional** Telegram Mini App surface served directly by the built-in API server. You do **not** need to clone or run the external `clawvader` miniapp repo at runtime.

## What it provides

When enabled, Hermes serves:

- `GET /miniapp`
- `GET /miniapp/`
- `GET /miniapp/index.html`
- `GET /api/model-info`
- `GET /api/session-usage`
- `GET /api/commands`
- `POST /api/command`
- existing `GET/POST/PATCH/DELETE /api/jobs...` routes
- existing `POST /v1/chat/completions`

The Mini App can authenticate with either:

- `Authorization: Bearer <API_SERVER_KEY>`
- `X-Telegram-Init-Data` from Telegram Mini Apps

## Prerequisites

You need:

1. A Telegram bot token (`TELEGRAM_BOT_TOKEN`)
2. At least one allowed Telegram user ID (`TELEGRAM_ALLOWED_USERS`)
3. The Hermes API server enabled
4. An HTTPS URL reachable by Telegram clients

## Enable the API server

Configure the API server in your active Hermes profile configuration. A minimal setup looks like:

```yaml
platforms:
  api_server:
    enabled: true
    extra:
      host: 127.0.0.1
      port: 8642
      key: sk-change-me
      telegram_miniapp_enabled: true
      cors_origins:
        - https://your-miniapp-domain.example
```

Or set equivalent environment variables in your active Hermes profile environment file:

```bash
API_SERVER_KEY=sk-change-me
API_SERVER_HOST=127.0.0.1
API_SERVER_PORT=8642
API_SERVER_TELEGRAM_MINIAPP_ENABLED=true
TELEGRAM_BOT_TOKEN=123456:ABCDEF...
TELEGRAM_ALLOWED_USERS=123456789
```

## One-command local launch

For local bring-up, Hermes now includes a helper launcher:

```bash
cd /opt/hermes-agent/source
scripts/run_telegram_miniapp_server.sh
```

By default it:
- loads your active Hermes profile environment
- enables the API server if needed
- defaults to `127.0.0.1:8765`
- enables the Telegram Mini App backend
- serves the bundled UI at `http://127.0.0.1:8765/miniapp/`

You can override the bind address or port with standard env vars such as:

```bash
API_SERVER_HOST=0.0.0.0 API_SERVER_PORT=8642 scripts/run_telegram_miniapp_server.sh
```

## Expose Hermes over HTTPS

Telegram Mini Apps run in the Telegram client and need HTTPS to reach Hermes from outside localhost.

Typical deployment patterns:

- reverse proxy Hermes behind Nginx/Caddy
- tunnel a local dev instance with something like Tailscale Funnel, Cloudflare Tunnel, or ngrok
- deploy Hermes on a public VPS with TLS termination

Make sure the public origin you use is also listed in `platforms.api_server.extra.cors_origins` (or `API_SERVER_CORS_ORIGINS`).

## Configure the BotFather menu button

In BotFather:

1. Open **/mybots**
2. Select your bot
3. Choose **Bot Settings → Menu Button**
4. Set the URL to your public Mini App entrypoint, for example:

```text
https://hermes.example.com/miniapp/
```

## How auth works

Hermes validates Telegram Mini App requests by verifying the `X-Telegram-Init-Data` signature against your configured `TELEGRAM_BOT_TOKEN`.

Access is still limited to your configured Telegram allowlist:

```bash
TELEGRAM_ALLOWED_USERS=123456789,987654321
```

If the Telegram signature is invalid, expired, or the Telegram user is not allowed, Hermes returns `401` JSON errors.

## Command and metadata endpoints

The current experimental Mini App backend exposes lightweight helper endpoints:

- `/api/model-info` — active model id, provider, context length
- `/api/session-usage` — cumulative token counters for the provided `X-Hermes-Session-Id`
- `/api/commands` — command palette metadata from the canonical Hermes command registry
- `/api/command` — executes a small safe subset of slash commands (`/help`, `/commands`, `/usage`, `/status`, `/profile`)

## Cron jobs from the Mini App

The Mini App reuses the existing API server cron routes:

- `GET /api/jobs`
- `POST /api/jobs`
- `GET /api/jobs/{job_id}`
- `PATCH /api/jobs/{job_id}`
- `DELETE /api/jobs/{job_id}`
- `POST /api/jobs/{job_id}/pause`
- `POST /api/jobs/{job_id}/resume`
- `POST /api/jobs/{job_id}/run`

## Troubleshooting

### `401 invalid_telegram_signature`

- confirm `TELEGRAM_BOT_TOKEN` matches the same bot that launched the Mini App
- confirm the request is forwarding `X-Telegram-Init-Data`
- confirm your reverse proxy is not stripping custom headers

### `401 telegram_user_not_allowed`

- add your numeric Telegram user ID to `TELEGRAM_ALLOWED_USERS`
- restart Hermes after changing env/config

### Mini App loads but API calls fail in the browser

- add your exact public origin to API server CORS origins
- ensure HTTPS is enabled end to end
- verify your proxy forwards `Authorization`, `X-Telegram-Init-Data`, and `X-Hermes-Session-Id`

## Caveats

This first-pass port is intentionally narrow:

- the frontend is a bundled single-file asset
- slash command execution is limited to a safe informational subset
- advanced theming and multi-user admin workflows are out of scope for now

That keeps the feature Hermes-native and dependency-free at runtime while the API surface stabilizes.
