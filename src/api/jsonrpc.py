import json

import ipfshttpclient
from ipfshttpclient.exceptions import DecodingError
from requests.exceptions import ReadTimeout
from sanic import Blueprint, Sanic, response
from sanic.log import logger
from sanic_jsonrpc import SanicJsonrpc

from src.pql.exceptions import PqlDecodingError
from src.pql.parser import parse_and_execute


def init_jsonrpc_endpoints(app: Sanic) -> None:
    """Initalizes JSON RPC endpoints

    Args:
        app (Sanic): Sanic app
    """
    jsonrpc = SanicJsonrpc(app, post_route="/rpc")

    @jsonrpc
    async def execute_pql(pql_json: str) -> str:
        """Execute PQL definition `pql_json` and return result.

        Args:
            pql_json (str): PQL definition JSON.

        Returns:
            str: result of the executed PQL JSON
        """
        logger.info(f"Execute PQL {pql_json} request.")
        req = json.loads(pql_json)

        res = await parse_and_execute(req)
        logger.info(f"Obtained result {res}")

        return res

    @jsonrpc
    async def execute_ipfs(ipfs_address: str, ipfs_hash: str) -> str:
        """Execute PQL definition located in IPFS.

        Args:
            ipfs_address (str): IPFS API address
            ipfs_hash (str): IPFS hash to execute

        Returns:
            str: result of the executed PQL JSON

        Raises:
            PqlDecodingError: file was not a JSON or IPFS was unreachable.
        """
        logger.info(f"Execute IPFS PQL {ipfs_address}/{ipfs_hash} request.")

        try:
            # Connect to the IPFS API server
            ipfs = ipfshttpclient.connect(ipfs_address)

            # Fetch the JSON from the hash
            req = ipfs.get_json(ipfs_hash, timeout=int(app.config["--timeout"]))
        except DecodingError:
            raise PqlDecodingError("object decoding error, expecting JSON format.")
        except ReadTimeout:
            raise PqlDecodingError("IPFS timed out before retrieving the file.")

        res = await parse_and_execute(req)
        logger.info(f"Obtained result {res}")

        return res
