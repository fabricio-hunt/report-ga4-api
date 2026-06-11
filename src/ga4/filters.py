"""GA4 dimension filter helpers."""

from google.analytics.data_v1beta.types import (
    Filter,
    FilterExpression,
    FilterExpressionList,
)


def or_filter(field: str, values: list[str]) -> FilterExpression:
    return FilterExpression(
        or_group=FilterExpressionList(
            expressions=[
                FilterExpression(
                    filter=Filter(
                        field_name=field,
                        string_filter=Filter.StringFilter(
                            match_type=Filter.StringFilter.MatchType.EXACT,
                            value=value,
                        ),
                    )
                )
                for value in values
            ]
        )
    )


def and_filter(*expressions: FilterExpression) -> FilterExpression:
    return FilterExpression(and_group=FilterExpressionList(expressions=list(expressions)))


def organic_filter(sources: list[str]) -> FilterExpression:
    return or_filter("sessionSourceMedium", sources)


def app_platform_filter() -> FilterExpression:
    return or_filter("platform", ["Android", "iOS"])


def web_platform_filter() -> FilterExpression:
    return or_filter("platform", ["web"])
