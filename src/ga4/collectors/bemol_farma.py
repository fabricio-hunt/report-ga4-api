"""Collect Bemol Farma organic metrics."""

import logging
from typing import Optional

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension, Metric, RunReportRequest

from src.config import Config
from src.ga4.filters import organic_filter
from src.ga4.processing import date_range, process_rows

logger = logging.getLogger("ga4")


def fetch_bemol_farma(client: BetaAnalyticsDataClient, config: Config) -> Optional[pd.DataFrame]:
    logger.info("Coletando: Bemol Farma (orgânico)")
    prop = f"properties/{config.properties['bemol_farma']}"
    dr = date_range(config.analysis_start, config.analysis_end)

    try:
        req = RunReportRequest(
            property=prop,
            dimensions=[Dimension(name="month"), Dimension(name="year")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="engagementRate"),
                Metric(name="totalRevenue"),
            ],
            date_ranges=[dr],
            dimension_filter=organic_filter(config.organic_sources_main),
        )
        resp = client.run_report(request=req)
        df = process_rows(
            resp.rows,
            {
                0: "Sessões orgânicas",
                1: "Usuários orgânicos",
                2: "Taxa de engajamento (%)",
                3: "Receita orgânica (R$)",
            },
        )
        if "Taxa de engajamento (%)" in df.columns:
            df["Taxa de engajamento (%)"] = (df["Taxa de engajamento (%)"] * 100).round(2)
        return df
    except Exception as exc:
        logger.error("Erro Bemol Farma: %s", exc)
        return None
