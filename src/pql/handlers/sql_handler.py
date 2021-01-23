import typing

import asyncpg

from src.pql.handlers.handler import Handler


class SqlHandler(Handler):
    """SqlHandler handles SQL requests."""

    @staticmethod
    async def execute(step: dict) -> typing.Any:
        """Handle SQL requests.

        Args:
            step: PQL step json.

        Returns:
            typing.Any: result
        """
        method = step["method"].split(".")[-1]

        if method == "postgres":
            conn = await asyncpg.connect(step["uri"])
            values = await conn.fetch(step["query"])

            await conn.close()

            return values
