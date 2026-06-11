"""Entrypoint for Bemol Farma Web organic report."""

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
from src.export.excel import export_bemol_app_report
from src.ga4.collectors.bemol_farma_web_organic import fetch_bemol_farma_web_organic
from src.io.paths import resolve_output_dir
from src.logging_setup import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="GA4 Farma Web Orgânico")
    add_common_args(parser)
    args = parser.parse_args()

    logger = setup_logging(log_file="ga4_collector.log")
    config = Config.from_env(profile="bemol_app")
    apply_period_overrides(config, args)

    output_dir = args.output_dir or resolve_output_dir()
    period_label = f"{config.analysis_start} a {config.analysis_end}"

    print(f"""
╔══════════════════════════════════════════════════════╗
║      GA4 Collector: Farma Web Orgânico — v5.4        ║
╠══════════════════════════════════════════════════════╣
║  Período: {config.analysis_start}  →  {config.analysis_end}  ║
╚══════════════════════════════════════════════════════╝
""")

    client = authenticate_ga4(config)
    if not client:
        logger.error("Falha na autenticação. Encerrando.")
        sys.exit(1)

    df_farma_web = fetch_bemol_farma_web_organic(client, config)
    path = export_bemol_app_report(
        df_farma_web,
        period_label=period_label,
        analysis_start=config.analysis_start,
        analysis_end=config.analysis_end,
        output_dir=output_dir,
    )

    if path:
        print(f"\nRelatório gerado com sucesso:\n   {path}\n")
    else:
        print("\nNenhum arquivo gerado. Verifique os logs.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
