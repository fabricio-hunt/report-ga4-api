"""Central configuration loaded from YAML and environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "default.yaml"


@lru_cache(maxsize=1)
def get_yaml_config() -> dict[str, Any]:
    with open(DEFAULT_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class Config:
    """Runtime configuration for GA4 collectors."""

    properties: dict[str, str] = field(default_factory=dict)
    organic_sources_main: list[str] = field(default_factory=list)
    organic_sources_bemol_app: list[str] = field(default_factory=list)

    analysis_start: str = "2026-05-01"
    analysis_end: str = "2026-05-31"
    analysis_start_2025: str = "2025-01-01"
    analysis_end_2025: str = "2025-12-31"
    analysis_start_2026: str = "2026-01-01"
    analysis_end_2026: str = "2026-05-31"

    client_secret_file: str = "client_secret.json"
    token_file: str = "token.pickle"
    scopes: list[str] = field(default_factory=list)
    secret_scope: str = "ga4-oauth"
    client_secret_key: str = "client_secret_json"
    refresh_token_key: str = "refresh_token"

    @classmethod
    def from_env(cls, profile: str = "main") -> Config:
        yaml_cfg = get_yaml_config()
        auth_cfg = yaml_cfg.get("auth", {})
        periods = yaml_cfg.get("periods", {}).get(profile, {})
        organic = yaml_cfg.get("organic_sources", {})

        cfg = cls(
            properties=yaml_cfg.get("properties", {}),
            organic_sources_main=organic.get("main", []),
            organic_sources_bemol_app=organic.get("bemol_app", []),
            client_secret_file=auth_cfg.get("client_secret_file", "client_secret.json"),
            token_file=auth_cfg.get("token_file", "token.pickle"),
            scopes=yaml_cfg.get("scopes", []),
            secret_scope=auth_cfg.get("secret_scope", "ga4-oauth"),
            client_secret_key=auth_cfg.get("client_secret_key", "client_secret_json"),
            refresh_token_key=auth_cfg.get("refresh_token_key", "refresh_token"),
        )

        if profile == "farma_comparacao":
            cfg.analysis_start_2025 = periods.get("analysis_start_2025", cfg.analysis_start_2025)
            cfg.analysis_end_2025 = periods.get("analysis_end_2025", cfg.analysis_end_2025)
            cfg.analysis_start_2026 = periods.get("analysis_start_2026", cfg.analysis_start_2026)
            cfg.analysis_end_2026 = periods.get("analysis_end_2026", cfg.analysis_end_2026)
        else:
            cfg.analysis_start = periods.get("analysis_start", cfg.analysis_start)
            cfg.analysis_end = periods.get("analysis_end", cfg.analysis_end)

        cfg.analysis_start = os.getenv("GA4_ANALYSIS_START", cfg.analysis_start)
        cfg.analysis_end = os.getenv("GA4_ANALYSIS_END", cfg.analysis_end)
        cfg.analysis_start_2025 = os.getenv("GA4_ANALYSIS_START_2025", cfg.analysis_start_2025)
        cfg.analysis_end_2025 = os.getenv("GA4_ANALYSIS_END_2025", cfg.analysis_end_2025)
        cfg.analysis_start_2026 = os.getenv("GA4_ANALYSIS_START_2026", cfg.analysis_start_2026)
        cfg.analysis_end_2026 = os.getenv("GA4_ANALYSIS_END_2026", cfg.analysis_end_2026)

        return cfg


def resolve_credential_path(filename: str) -> str:
    """Resolve credential file path relative to project root."""
    path = Path(filename)
    if path.is_absolute():
        return str(path)
    return str(PROJECT_ROOT / filename)
