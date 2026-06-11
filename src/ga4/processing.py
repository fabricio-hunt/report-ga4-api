"""Convert GA4 API rows into pandas DataFrames."""

import pandas as pd
from google.analytics.data_v1beta.types import DateRange

MONTH_NAMES = {
    "01": "Janeiro",
    "02": "Fevereiro",
    "03": "Março",
    "04": "Abril",
    "05": "Maio",
    "06": "Junho",
    "07": "Julho",
    "08": "Agosto",
    "09": "Setembro",
    "10": "Outubro",
    "11": "Novembro",
    "12": "Dezembro",
}


def process_rows(rows, metric_map: dict[int, str]) -> pd.DataFrame:
    records = []
    for row in rows:
        dims = [d.value for d in row.dimension_values]
        month_num = dims[0]
        year = dims[1]

        record = {
            "Mês": MONTH_NAMES.get(month_num, month_num),
            "Nº Mês": month_num,
            "Ano": year,
        }
        for pos, col_name in metric_map.items():
            raw = row.metric_values[pos].value
            record[col_name] = float(raw) if "." in raw else int(raw)
        records.append(record)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.sort_values(["Ano", "Nº Mês"]).reset_index(drop=True)
    return df.drop(columns=["Nº Mês"])


def date_range(start: str, end: str) -> DateRange:
    return DateRange(start_date=start, end_date=end)
