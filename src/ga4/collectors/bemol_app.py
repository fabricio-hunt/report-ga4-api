"""Collect Bemol App organic + total metrics."""

import logging
from typing import Optional

import pandas as pd
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import Dimension, Metric, RunReportRequest

from src.config import Config
from src.ga4.filters import and_filter, app_platform_filter, organic_filter
from src.ga4.processing import date_range, process_rows

logger = logging.getLogger("ga4")


def fetch_bemol_app(client: BetaAnalyticsDataClient, config: Config) -> Optional[pd.DataFrame]:
    logger.info("Coletando: Bemol App (Android + iOS)")
    prop = f"properties/{config.properties['ecommerce_bemol']}"
    dr = date_range(config.analysis_start, config.analysis_end)

    try:
        req_org = RunReportRequest(
            property=prop,
            dimensions=[Dimension(name="month"), Dimension(name="year")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="newUsers"),
                Metric(name="transactions"),
                Metric(name="totalRevenue"),
            ],
            date_ranges=[dr],
            dimension_filter=and_filter(
                app_platform_filter(),
                organic_filter(config.organic_sources_main),
            ),
        )
        resp_org = client.run_report(request=req_org)
        df_org = process_rows(
            resp_org.rows,
            {
                0: "Sessões organic",
                1: "Usuários ativos organic",
                2: "Novos usuários organic",
                3: "Transações",
                4: "Receita organic (R$)",
            },
        )

        req_tot = RunReportRequest(
            property=prop,
            dimensions=[Dimension(name="month"), Dimension(name="year")],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions"),
                Metric(name="transactions"),
                Metric(name="totalRevenue"),
            ],
            date_ranges=[dr],
            dimension_filter=app_platform_filter(),
        )
        resp_tot = client.run_report(request=req_tot)
        df_tot = process_rows(
            resp_tot.rows,
            {
                0: "App Usuários ativos total",
                1: "App Sessões total",
                2: "App Transações total",
                3: "App Receita total (R$)",
            },
        )

        return df_org.merge(df_tot, on=["Mês", "Ano"], how="outer")
    except Exception as exc:
        logger.error("Erro Bemol App: %s", exc)
        return None
