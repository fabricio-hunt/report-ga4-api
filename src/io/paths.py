"""Resolve output paths by runtime environment."""

import os
from pathlib import Path

from src.config import get_yaml_config

LOCAL_DEFAULT_OUTPUT = (
    r"C:\Users\fabricio.barauna\OneDrive - BEMOL S A\Documentos"
)


def is_databricks() -> bool:
    """Return True when running inside a Databricks workspace."""
    if os.getenv("GA4_ENV", "").lower() == "databricks":
        return True
    return bool(os.getenv("DATABRICKS_RUNTIME_VERSION"))


def resolve_output_dir() -> str:
    """Return the directory where Excel reports should be written."""
    override = os.getenv("GA4_OUTPUT_DIR")
    if override:
        output_dir = override
    elif is_databricks():
        yaml_cfg = get_yaml_config()
        output_dir = yaml_cfg.get("output", {}).get(
            "databricks_default",
            "/Volumes/<catalog>/<schema>/<volume>/ga4_reports",
        )
    else:
        yaml_cfg = get_yaml_config()
        output_dir = yaml_cfg.get("output", {}).get("local_default", LOCAL_DEFAULT_OUTPUT)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return output_dir
