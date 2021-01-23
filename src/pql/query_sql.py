import typing

import pandas as pd
from pandasql import sqldf

from src.pql.exceptions import ParseDataError, UserQueryError


def to_df(data: typing.Any, parser: typing.Optional[str]) -> pd.DataFrame:
    """Convert data to pd.DataFrame.

    Args:
        data (typing.Any): The data to convert to pd.DataFrame.
        parser (str): The parser required to convert data to pd.DataFrame.

    Returns:
        pd.DataFrame: the data in pd.DataFrame format
    """
    try:
        if parser == "json":
            return pd.json_normalize(data)
        elif parser == "list":
            return pd.DataFrame([data])
        if parser is None:
            return data
    except Exception:
        raise ParseDataError(f"failed to parse data {data} using parser {parser}")


async def execute_sql_query(
    request_data: dict, query: str, result: typing.Optional[bool]
) -> typing.Any:
    """Execute user defined query against request data.

    Args:
        request_data: dictionary containing request data formatted as pd.DataFrame.
        query: user defined query to run against request data.
        result: bool indicating if the query response is the final result.

    Returns:
        typing.Any: sql query result
    """
    try:
        if result:
            return sqldf(query, request_data).iloc[0, 0]
        else:
            return sqldf(query, request_data)
    except Exception:
        raise UserQueryError(f"failed to run query: {query[:100]}...")


def construct_aggregate_sql_payload(pipelines: list, parsers: list) -> dict:
    """parses pipeline results into a pd.DataFrame and formats appropriately for
    downstream processing.

    Args:
        pipelines (list): list of pipelines as associated with PQL query
        parsers (list): list of parsers required to convert pipeline results to
        pd.DataFrame

    Returns:
        dict: returns an appropriately structured dictionary containing pipeline
        results as pd.DataFrame for downstream processing
    """
    return {
        f"result_{i}": to_df(pipeline.step_results[-1], parsers[i])
        for i, pipeline in enumerate(pipelines)
    }
