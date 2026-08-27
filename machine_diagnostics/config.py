"""Configuration loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_TOOLS = ["git", "python", "pip", "node", "npm", "docker"]


class ConfigError(ValueError):
    """Raised when a configuration file is invalid."""


def load_config(path: str | None) -> Dict[str, Any]:
    if path is None:
        return {"developer_tools": DEFAULT_TOOLS.copy()}

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Configuration path does not exist: {config_path}")
    if not config_path.is_file():
        raise ConfigError(f"Configuration path is not a file: {config_path}")

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Malformed JSON configuration: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Configuration root must be a JSON object.")

    tools = data.get("developer_tools", DEFAULT_TOOLS)
    if not isinstance(tools, list) or not all(isinstance(x, str) and x.strip() for x in tools):
        raise ConfigError("'developer_tools' must be a list of non-empty strings.")

    return {"developer_tools": tools}
