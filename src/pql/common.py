import typing

import pandas as pd
from pandasql import sqldf

from src.pql.exceptions import UserQueryError, ParserNotFound


def to_df(data: typing.Any, parser: typing.Optional[str]) -> pd.DataFrame:
    """Convert data to pd.DataFrame.

    Args:
        data: The data to convert to pd.DataFrame.
        parser: The parser required to convert data to pd.DataFrame.

    """
    if parser == "json":
        return pd.json_normalize(data)
    if parser == "list":
        return pd.DataFrame([data])
    if parser is None:
        return data
    else:
        raise ParserNotFound(f"parser not found - {parser}")


async def execute_user_query(
    request_data: dict, query: str, result: typing.Optional[bool]
) -> typing.Any:
    """Execute user defined query against request data.

    Args:
        request_data: dictionary containing request data formatted as pd.DataFrame.
        query: user defined query to run against request data.
        result: index of the result.
    """
    try:
        if result:
            return sqldf(query, request_data).iloc[0, 0]
        else:
            return sqldf(query, request_data)
    except Exception:
        raise UserQueryError(f"failed to run query: {query[:100]}...")
