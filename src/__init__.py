import asyncio
import json

import ipfshttpclient
from ipfshttpclient.exceptions import DecodingError
from requests.exceptions import ReadTimeout
from sanic import Sanic, response
from sanic.log import logger
from sanic_cors import CORS
from sanic_jsonrpc import SanicJsonrpc
from sanic_session import InMemorySessionInterface

from src.config import config
from src.logging import DEFAULT_LOGGING_CONFIG
from src.models import db
from src.network import chains
from src.pql.exceptions import PqlDecodingError
from src.pql.parser import parse_and_execute


def create_app(args={}) -> Sanic:  # noqa: C901
    app = Sanic("src", log_config=DEFAULT_LOGGING_CONFIG)
    app.config.from_object(config)
    app.update_config(args)

    jsonrpc = SanicJsonrpc(app, post_route="/rpc", ws_route="/ws")
    CORS(app)

    if app.config["ENABLE_DATABASE"]:
        asyncio.get_event_loop().run_until_complete(
            db.set_bind(app.config["DATABASE_URL"])
        )

    # Set UI
    session = InMemorySessionInterface(cookie_name=app.name, prefix=app.name)

    if app.config["ENABLE_BACKGROUND_WORKER"]:
        from src.process.collector import start_collecting

        asyncio.get_event_loop().run_until_complete(start_collecting(chains))

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
            req = ipfs.get_json(ipfs_hash, timeout=int(args["--timeout"]))
        except DecodingError:
            raise PqlDecodingError("object decoding error, expecting JSON format.")
        except ReadTimeout:
            raise PqlDecodingError("IPFS timed out before retrieving the file.")

        res = await parse_and_execute(req)
        logger.info(f"Obtained result {res}")

        return res

    @app.middleware("request")
    async def add_session_to_request(request):
        """Adds session to the request.

        Args:
            request: request object
        """
        await session.open(request)

    @app.middleware("response")
    async def save_session(request, response):
        """Saves session to the response.

        Args:
            request: request object.
            response: response object.
        """
        await session.save(request, response)

    @app.route("/api/ipfs")
    async def api_ipfs_list(request):
        """Lists local IPFS hashes.

        Args:
            request: request
        """
        # Connect to the IPFS API server
        ipfs = ipfshttpclient.connect(app.config["IPFS_API_SERVER_ADDRESS"])
        hashes = [key for key in ipfs.pin.ls(type="recursive")["Keys"].keys()]

        return response.json({"hashes": hashes})

    @app.route("api/ipfs/<ipfs_hash>")
    async def api_ipfs_hash(request, ipfs_hash: str):
        """Get PQL contents in `ipfs_hash`, return error if not valid PQL.

        Args:
            ipfs_hash: PQL JSON
        """
        if ipfs_hash == "new":
            return response.json(
                {
                    "pql": app.config["TEMPLATE_PQL_DEFINITION"],
                    "hash": "New PQL definition",
                }
            )

        ipfs = ipfshttpclient.connect(app.config["IPFS_API_SERVER_ADDRESS"])

        try:
            js = ipfs.get_json(ipfs_hash, timeout=int(args["--timeout"]))

            return response.json({"pql": js, "hash": ipfs_hash})
        except DecodingError:
            return response.json({"error": "Not a JSON file."}, status=400)
        except Exception:
            return response.json({"error": "Not a file."}, status=400)

    @app.post("/api/test_pql")
    async def test_pql(request):
        """Runs given PQL JSON `request` and returns result.

        Args:
            request: PQL JSON
        """
        pql = request.json

        try:
            res = await parse_and_execute(pql)
            return response.json({"result": res})
        except Exception as e:
            if hasattr(e, "message"):
                return response.json({"error": e.message})
            else:
                return response.json({"error": str(e)})

    @app.post("/api/save_pql")
    async def save_pql(request):
        """Saves given JSON `request` and returns successful JSON.

        Args:
            request: PQL JSON
        """
        pql = request.json

        try:
            ipfs = ipfshttpclient.connect(app.config["IPFS_API_SERVER_ADDRESS"])
            ipfs_hash = ipfs.add_json(pql)

            return response.json(
                {"success": f"Saving was successful, hash: {ipfs_hash}"}
            )
        except Exception as e:
            return response.json({"error": e.message})

    @app.get("/add_contract_oracle/<address>")
    async def add_contract_oracle(request, address: str):
        """Adds a contract to be tracked by the node.

        Args:
            request:
            address (str): address to be tracked
        """
        from src.models import ContractOracle

        await ContractOracle.create(id=address, active=True)
        return response.json({"result": "ok"})

    return app
