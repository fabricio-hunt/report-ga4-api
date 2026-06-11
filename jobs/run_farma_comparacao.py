"""Entrypoint for Bemol Farma Web total YoY comparison report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.auth import authenticate_ga4
from src.cli import add_farma_comparacao_args, apply_period_overrides
from src.config import Config
from src.export.excel import export_farma_comparacao_report
from src.ga4.collectors.farma_comparacao import fetch_farma_comparacao
from src.io.paths import resolve_output_dir
from src.logging_setup import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="GA4 Farma Web Total — comparativo YoY")
    add_farma_comparacao_args(parser)
    args = parser.parse_args()

    logger = setup_logging(log_file="ga4_farma_collector.log")
    config = Config.from_env(profile="farma_comparacao")
    apply_period_overrides(config, args, profile="farma_comparacao")

    output_dir = args.output_dir or resolve_output_dir()
    period_label = (
        f"{config.analysis_start_2025} a {config.analysis_end_2025}"
        f"  |  {config.analysis_start_2026} a {config.analysis_end_2026}"
    )

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║      GA4 Collector — v6.0 (Bemol Farma Web Total)            ║
╠══════════════════════════════════════════════════════════════╣
║  Farma : {config.analysis_start_2025}  →  {config.analysis_end_2025}  (2025)  ║
║          {config.analysis_start_2026}  →  {config.analysis_end_2026}  (2026)  ║
╚══════════════════════════════════════════════════════════════╝
""")

    client = authenticate_ga4(config)
    if not client:
        logger.error("Falha na autenticação. Encerrando.")
        sys.exit(1)

    df_farma = fetch_farma_comparacao(client, config)
    path = export_farma_comparacao_report(
        df_farma,
        period_label=period_label,
        output_dir=output_dir,
    )

    if path:
        print(f"\nRelatório gerado com sucesso:\n   {path}\n")
    else:
        print("\nNenhum arquivo gerado. Verifique os logs.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
