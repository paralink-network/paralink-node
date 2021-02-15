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

from src.api import ipfs_bp
from src.config import config
from src.logging import DEFAULT_LOGGING_CONFIG
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
        setup_database(app)

    # Set UI
    session = InMemorySessionInterface(cookie_name=app.name, prefix=app.name)

    if app.config["ENABLE_BACKGROUND_WORKER"]:
        from src.process.collector import start_collecting

        asyncio.get_event_loop().run_until_complete(start_collecting(chains))

    app.blueprint(ipfs_bp)

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


def setup_database(app: Sanic):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_async_engine(
        app.config.DATABASE_URL,
        echo=True,
    )

    @app.listener("before_server_start")
    async def connect_to_db(*args, **kwargs):
        app.db = scoped_session(
            sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        )()

    @app.listener("after_server_stop")
    async def disconnect_from_db(*args, **kwargs):
        await app.db.close()
