import typing

from paranode.pql.parser import Parser


async def parse_and_execute(pql: dict) -> typing.Any:
    """parse_and_execute parses the initial PQL version and selects the correct Parser
    class.

    Args:
        pql (dict): a valid PQL JSON

    Returns:
        typing.Any: executed result
    """
    return await Parser(pql).execute()

