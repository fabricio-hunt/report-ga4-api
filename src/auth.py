"""GA4 authentication for local OAuth and Databricks Secrets."""

from __future__ import annotations

import json
import logging
import pickle
from typing import Optional

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src.config import Config, resolve_credential_path
from src.io.paths import is_databricks

logger = logging.getLogger("ga4")


def _get_dbutils():
    try:
        from pyspark.dbutils import DBUtils
        from pyspark.sql import SparkSession

        return DBUtils(SparkSession.builder.getOrCreate())
    except Exception:
        import IPython

        return IPython.get_ipython().user_ns.get("dbutils")


def _credentials_from_refresh_token(
    client_config: dict,
    refresh_token: str,
    scopes: list[str],
) -> Credentials:
    client_info = client_config.get("installed") or client_config.get("web") or client_config
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri=client_info["token_uri"],
        client_id=client_info["client_id"],
        client_secret=client_info["client_secret"],
        scopes=scopes,
    )
    creds.refresh(Request())
    return creds


def _authenticate_local(config: Config) -> Optional[Credentials]:
    token_path = resolve_credential_path(config.token_file)
    secret_path = resolve_credential_path(config.client_secret_file)

    creds = None
    try:
        with open(token_path, "rb") as f:
            creds = pickle.load(f)
    except FileNotFoundError:
        pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secret_path, config.scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return creds


def _authenticate_databricks(config: Config) -> Optional[Credentials]:
    dbutils = _get_dbutils()
    client_secret_json = dbutils.secrets.get(config.secret_scope, config.client_secret_key)
    refresh_token = dbutils.secrets.get(config.secret_scope, config.refresh_token_key)
    client_config = json.loads(client_secret_json)
    return _credentials_from_refresh_token(client_config, refresh_token, config.scopes)


def authenticate_ga4(config: Config) -> Optional[BetaAnalyticsDataClient]:
    """Return an authenticated GA4 client for the current runtime."""
    try:
        if is_databricks():
            creds = _authenticate_databricks(config)
        else:
            creds = _authenticate_local(config)
        return BetaAnalyticsDataClient(credentials=creds)
    except Exception as exc:
        logger.error("Erro na autenticação: %s", exc)
        return None
