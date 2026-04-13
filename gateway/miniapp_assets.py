from __future__ import annotations

from importlib import resources
from pathlib import Path

from hermes_constants import get_hermes_home

_MINIAPP_SUBDIR = Path("static") / "telegram_miniapp"


def resolve_miniapp_asset_path(asset_name: str = "index.html") -> Path:
    override_path = get_hermes_home() / "miniapp" / asset_name
    if override_path.exists() and override_path.is_file():
        return override_path

    resource = resources.files("gateway").joinpath(str(_MINIAPP_SUBDIR / asset_name))
    return Path(str(resource))


def read_miniapp_asset(asset_name: str = "index.html") -> bytes:
    return resolve_miniapp_asset_path(asset_name).read_bytes()
