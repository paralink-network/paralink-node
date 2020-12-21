import json
import typing

import aiohttp

from src.pql.handlers.handler import Handler
from src.pql.exceptions import MethodNotFound


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
                    data = await resp.read()

                    return json.loads(data)
        elif method == "post":
            async with aiohttp.ClientSession() as session:
                async with session.post(step["uri"], json=step["params"]) as resp:
                    data = await resp.read()
                    return json.loads(data)
        else:
            raise MethodNotFound(f'handler for HTTP method "{method}" not found.')

