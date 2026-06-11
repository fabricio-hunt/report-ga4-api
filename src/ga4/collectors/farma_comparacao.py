"""Collect Bemol Farma Web total metrics with YoY comparison."""

import logging
from typing import Optional

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension, Metric, RunReportRequest

from src.config import Config
from src.ga4.filters import web_platform_filter
from src.ga4.processing import MONTH_NAMES, date_range, process_rows

logger = logging.getLogger("ga4")


def fetch_farma_comparacao(
    client: BetaAnalyticsDataClient, config: Config
) -> Optional[pd.DataFrame]:
    logger.info("Coletando: Bemol Farma (Web Total) — 2025 e 2026")
    prop = f"properties/{config.properties['bemol_farma']}"
    dimension_filter = web_platform_filter()

    def _fetch_period(start: str, end: str, suffix: str) -> Optional[pd.DataFrame]:
        try:
            req = RunReportRequest(
                property=prop,
                dimensions=[Dimension(name="month"), Dimension(name="year")],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers"),
                    Metric(name="engagementRate"),
                    Metric(name="totalRevenue"),
                    Metric(name="transactions"),
                ],
                date_ranges=[date_range(start, end)],
                dimension_filter=dimension_filter,
            )
            resp = client.run_report(request=req)
            return process_rows(
                resp.rows,
                {
                    0: f"Farma_Sessões_Totais_{suffix}",
                    1: f"Farma_Usuários_totais_{suffix}",
                    2: f"Farma_Engajamento_total_{suffix}",
                    3: f"Farma_Receita_total_{suffix}",
                    4: f"Farma_Transações_total_{suffix}",
                },
            )
        except Exception as exc:
            logger.error("Erro Farma %s: %s", suffix, exc)
            return None

    df_2025 = _fetch_period(
        config.analysis_start_2025, config.analysis_end_2025, "2025"
    )
    df_2026 = _fetch_period(
        config.analysis_start_2026, config.analysis_end_2026, "2026"
    )

    frames = []
    if df_2025 is not None and not df_2025.empty:
        frames.append(df_2025)
    if df_2026 is not None and not df_2026.empty:
        frames.append(df_2026)

    if not frames:
        logger.warning("Farma: nenhum dado retornado para nenhum dos períodos.")
        return None

    df_all = pd.concat(frames, ignore_index=True, sort=False)
    month_order = {v: k for k, v in MONTH_NAMES.items()}
    df_all["_sort_mes"] = df_all["Mês"].map(month_order)
    df_all["_sort_ano"] = df_all["Ano"].astype(str)

    base_metrics = [
        "Farma_Sessões_Totais",
        "Farma_Usuários_totais",
        "Farma_Engajamento_total",
        "Farma_Receita_total",
        "Farma_Transações_total",
    ]

    for metric in base_metrics:
        col_25 = f"{metric}_2025"
        col_26 = f"{metric}_2026"
        df_all[metric] = df_all.get(col_25, pd.NA).fillna(df_all.get(col_26, pd.NA))

    df_final = df_all[["Ano", "Mês", "_sort_ano", "_sort_mes"] + base_metrics].copy()
    df_final = df_final.sort_values(["_sort_ano", "_sort_mes"]).reset_index(drop=True)
    df_final = df_final.drop(columns=["_sort_ano", "_sort_mes"])

    logger.info(
        "Farma coletado: %s meses em 2025 | %s meses em 2026",
        len(df_2025) if df_2025 is not None else 0,
        len(df_2026) if df_2026 is not None else 0,
    )
    return df_final
