"""Logging setup for local and Databricks runtimes."""

import logging
import sys

from src.io.paths import is_databricks, resolve_output_dir


def setup_logging(name: str = "ga4", log_file: str | None = None) -> logging.Logger:
    """Configure logging. File handler is used only in local runs."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if not is_databricks() and log_file:
        import os

        output_dir = resolve_output_dir()
        log_path = os.path.join(output_dir, log_file)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
