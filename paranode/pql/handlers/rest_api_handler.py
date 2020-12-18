import typing

import aiohttp
from sanic_jsonrpc.errors import Error

from .handler import Handler


class RestApiHandler(Handler):
    """RestApiHandler handles HTTP requests."""

    @staticmethod
    async def execute(step: dict) -> typing.Any:
        """Handle HTTP requests.

        Args:
            step: PQL step json.

        Returns:
            typing.Any: result
        """
        method = step["method"].split(".")[-1]

        if method == "get":
            async with aiohttp.ClientSession() as session:
                async with session.get(step["uri"]) as resp:
                    return await resp.json()
        else:
            raise Error(-32010, f'handler for HTTP method "{method}" not found.')

