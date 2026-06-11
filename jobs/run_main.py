"""Entrypoint for the main GA4 report (Web + Farma + App)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.auth import authenticate_ga4
from src.cli import add_common_args, apply_period_overrides
from src.config import Config
from src.export.excel import export_main_report
from src.ga4.collectors.bemol_app import fetch_bemol_app
from src.ga4.collectors.bemol_farma import fetch_bemol_farma
from src.ga4.collectors.bemol_web import fetch_bemol_web
from src.io.paths import resolve_output_dir
from src.logging_setup import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="GA4 Collector Bemol — relatório principal")
    add_common_args(parser)
    args = parser.parse_args()

    logger = setup_logging(log_file="ga4_collector.log")
    config = Config.from_env(profile="main")
    apply_period_overrides(config, args)

    output_dir = args.output_dir or resolve_output_dir()
    period_label = f"{config.analysis_start} a {config.analysis_end}"

    print(f"""
╔══════════════════════════════════════════════════╗
║      GA4 Collector Bemol — v5.0 (Mensal)         ║
╠══════════════════════════════════════════════════╣
║  Período: {config.analysis_start}  →  {config.analysis_end}  ║
╚══════════════════════════════════════════════════╝
""")

    client = authenticate_ga4(config)
    if not client:
        logger.error("Falha na autenticação. Encerrando.")
        sys.exit(1)

    df_web = fetch_bemol_web(client, config)
    df_farma = fetch_bemol_farma(client, config)
    df_app = fetch_bemol_app(client, config)

    path = export_main_report(
        df_web,
        df_farma,
        df_app,
        period_label=period_label,
        analysis_start=config.analysis_start,
        output_dir=output_dir,
    )

    if path:
        print(f"\nRelatório gerado com sucesso:\n   {path}\n")
    else:
        print("\nNenhum arquivo gerado. Verifique os logs.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
