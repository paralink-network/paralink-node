import typing

import pandas as pd
from pandasql import sqldf

from src.pql.exceptions import ParseDataError, UserQueryError


def prepare_data(
    data: typing.Any, parser: typing.Union[str, list, None] = None
) -> dict:
    """Convert data to pd.DataFrame.

    Args:
        data (typing.Any): The data to convert to pd.DataFrame.
        parser (Union[str, list]): The parser(s) required to convert data to pd.DataFrame.

    Returns:
        pd.DataFrame: the data in pd.DataFrame format
    """
    methods = {
        "json": lambda x: pd.json_normalize(x),
        "list": lambda x: pd.DataFrame([x]),
        "dict": lambda x: pd.DataFrame.from_dict(x),
        None: lambda x: x,
    }

    try:
        if isinstance(parser, list):
            return {
                key: methods[parser[i]](value)
                for i, (key, value) in enumerate(data.items())
            }
        else:
            return {"data": methods[parser](data)}
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
