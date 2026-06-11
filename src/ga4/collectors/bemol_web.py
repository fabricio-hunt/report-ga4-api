"""Collect Bemol Web organic + total metrics."""

import logging
from typing import Optional

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension, Metric, RunReportRequest

from src.config import Config
from src.ga4.filters import and_filter, organic_filter, web_platform_filter
from src.ga4.processing import date_range, process_rows

logger = logging.getLogger("ga4")


def fetch_bemol_web(client: BetaAnalyticsDataClient, config: Config) -> Optional[pd.DataFrame]:
    logger.info("Coletando: Bemol Web (orgânico)")
    prop = f"properties/{config.properties['ecommerce_bemol']}"
    dr = date_range(config.analysis_start, config.analysis_end)

    try:
        req_org = RunReportRequest(
            property=prop,
            dimensions=[Dimension(name="month"), Dimension(name="year")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="engagementRate"),
                Metric(name="totalRevenue"),
            ],
            date_ranges=[dr],
            dimension_filter=and_filter(
                web_platform_filter(),
                organic_filter(config.organic_sources_main),
            ),
        )
        resp_org = client.run_report(request=req_org)
        df_org = process_rows(
            resp_org.rows,
            {
                0: "Sessões orgânicas",
                1: "Usuários orgânicos",
                2: "Taxa de engajamento (%)",
                3: "Receita orgânica (R$)",
            },
        )
        if "Taxa de engajamento (%)" in df_org.columns:
            df_org["Taxa de engajamento (%)"] = (
                df_org["Taxa de engajamento (%)"] * 100
            ).round(2)

        req_tot = RunReportRequest(
            property=prop,
            dimensions=[Dimension(name="month"), Dimension(name="year")],
            metrics=[Metric(name="sessions"), Metric(name="totalRevenue")],
            date_ranges=[dr],
            dimension_filter=web_platform_filter(),
        )
        resp_tot = client.run_report(request=req_tot)
        df_tot = process_rows(
            resp_tot.rows,
            {
                0: "Sessões totais (todos os canais)",
                1: "Receita total (todos os canais) (R$)",
            },
        )

        return df_org.merge(df_tot, on=["Mês", "Ano"], how="outer")
    except Exception as exc:
        logger.error("Erro Bemol Web: %s", exc)
        return None
