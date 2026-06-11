"""Collect Bemol Farma Web organic metrics (auxiliary report)."""

import logging
from typing import Optional

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension, Metric, RunReportRequest

from src.config import Config
from src.ga4.filters import and_filter, organic_filter, web_platform_filter
from src.ga4.processing import date_range, process_rows

logger = logging.getLogger("ga4")


def fetch_bemol_farma_web_organic(
    client: BetaAnalyticsDataClient, config: Config
) -> Optional[pd.DataFrame]:
    logger.info("Coletando: Bemol Farma (Web + Orgânico)")
    prop = f"properties/{config.properties['bemol_farma']}"
    dr = date_range(config.analysis_start, config.analysis_end)

    try:
        req = RunReportRequest(
            property=prop,
            dimensions=[Dimension(name="month"), Dimension(name="year")],
            metrics=[
                Metric(name="totalUsers"),
                Metric(name="sessions"),
                Metric(name="transactions"),
                Metric(name="totalRevenue"),
                Metric(name="engagementRate"),
            ],
            date_ranges=[dr],
            dimension_filter=and_filter(
                web_platform_filter(),
                organic_filter(config.organic_sources_bemol_app),
            ),
        )
        resp = client.run_report(request=req)
        df = process_rows(
            resp.rows,
            {
                0: "Farma Web Total de Usuários",
                1: "Farma Web Sessões",
                2: "Farma Web Transações",
                3: "Farma Web Receita (R$)",
                4: "Farma Web Engajamento (%)",
            },
        )

        if "Farma Web Engajamento (%)" in df.columns:
            df["Farma Web Engajamento (%)"] = (
                df["Farma Web Engajamento (%)"] * 100
            ).round(2)

        col_order = [
            "Ano",
            "Mês",
            "Farma Web Total de Usuários",
            "Farma Web Sessões",
            "Farma Web Transações",
            "Farma Web Receita (R$)",
            "Farma Web Engajamento (%)",
        ]
        return df[[c for c in col_order if c in df.columns]]
    except Exception as exc:
        logger.error("Erro Bemol Farma Web: %s", exc)
        return None
