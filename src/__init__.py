import json

from requests.exceptions import ReadTimeout
from sanic import Sanic
from sanic.log import logger
from sanic_jsonrpc import SanicJsonrpc

import ipfshttpclient

from src.pql.parser import parse_and_execute
from src.pql.exceptions import PqlDecodingError


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

    @jsonrpc
    async def execute_ipfs(ipfs_address: str, ipfs_hash: str) -> str:
        logger.info(f"Execute IPFS PQL {ipfs_address}/{ipfs_hash} request.")

        try:
            # Connect to the IPFS API server
            ipfs = ipfshttpclient.connect(ipfs_address)

            # Fetch the JSON from the hash
            req = ipfs.get_json(ipfs_hash, timeout=args.timeout)
        except ipfshttpclient.expections.DecodingError:
            raise PqlDecodingError("object decoding error, expecting JSON format.")
        except ReadTimeout:
            raise PqlDecodingError("IPFS timed out before retrieving the file.")

        res = await parse_and_execute(req)
        logger.info(f"Obtained result {res}")

        return res

    return app
