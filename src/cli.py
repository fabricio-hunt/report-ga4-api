"""Shared CLI argument parsing for job entrypoints."""

from __future__ import annotations

import argparse
import os


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--analysis-start",
        default=os.getenv("GA4_ANALYSIS_START"),
        help="Data inicial (YYYY-MM-DD). Default: config/default.yaml ou GA4_ANALYSIS_START",
    )
    parser.add_argument(
        "--analysis-end",
        default=os.getenv("GA4_ANALYSIS_END"),
        help="Data final (YYYY-MM-DD). Default: config/default.yaml ou GA4_ANALYSIS_END",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("GA4_OUTPUT_DIR"),
        help="Diretório de saída Excel. Default: resolve_output_dir()",
    )


def add_farma_comparacao_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--analysis-start-2025",
        default=os.getenv("GA4_ANALYSIS_START_2025"),
        help="Início do período 2025 (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--analysis-end-2025",
        default=os.getenv("GA4_ANALYSIS_END_2025"),
        help="Fim do período 2025 (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--analysis-start-2026",
        default=os.getenv("GA4_ANALYSIS_START_2026"),
        help="Início do período 2026 (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--analysis-end-2026",
        default=os.getenv("GA4_ANALYSIS_END_2026"),
        help="Fim do período 2026 (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--output-dir",
        default=os.getenv("GA4_OUTPUT_DIR"),
        help="Diretório de saída Excel. Default: resolve_output_dir()",
    )


def apply_period_overrides(config, args, profile: str = "main") -> None:
    if profile == "farma_comparacao":
        if args.analysis_start_2025:
            config.analysis_start_2025 = args.analysis_start_2025
        if args.analysis_end_2025:
            config.analysis_end_2025 = args.analysis_end_2025
        if args.analysis_start_2026:
            config.analysis_start_2026 = args.analysis_start_2026
        if args.analysis_end_2026:
            config.analysis_end_2026 = args.analysis_end_2026
    else:
        if args.analysis_start:
            config.analysis_start = args.analysis_start
        if args.analysis_end:
            config.analysis_end = args.analysis_end
