import json

from sanic import Sanic
from sanic.log import logger
from sanic_jsonrpc import SanicJsonrpc

from paranode.pql import parse_and_execute


def create_app(args) -> Sanic:
    app = Sanic("paralink-node")
    jsonrpc = SanicJsonrpc(app, post_route="/rpc", ws_route="/ws")

    @jsonrpc
    async def execute_pql(pql_json: str) -> str:
        logger.info(f"Execute PQL {pql_json} request.")
        req = json.loads(pql_json)

        res = await parse_and_execute(req)
        logger.info(f"Obtained result {res}")

        return res

    return app
