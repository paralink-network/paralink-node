import json

from requests.exceptions import ReadTimeout
from sanic import Sanic
from sanic import response
from sanic.log import logger
from sanic_jsonrpc import SanicJsonrpc
from sanic_session import InMemorySessionInterface
from sanic_jinja2 import SanicJinja2

import ipfshttpclient
from ipfshttpclient.exceptions import DecodingError

from src.config import config
from src.pql.parser import parse_and_execute
from src.pql.exceptions import PqlDecodingError


def create_app(args, environment="development") -> Sanic:
    app = Sanic("src")
    app.config.from_object(config[environment])

    jsonrpc = SanicJsonrpc(app, post_route="/rpc", ws_route="/ws")

    # Set UI
    jinja = SanicJinja2(app)
    session = InMemorySessionInterface(cookie_name=app.name, prefix=app.name)

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
        await session.open(request)

    @app.middleware("response")
    async def save_session(request, response):
        await session.save(request, response)

    @app.route("/")
    @app.route("/ipfs")
    @jinja.template("ipfs.html")  # decorator method is staticmethod
    async def ipfs(request):
        # Connect to the IPFS API server
        ipfs = ipfshttpclient.connect(app.config["IPFS_API_SERVER_ADDRESS"])
        hashes = [key for key in ipfs.pin.ls(type="recursive")["Keys"].keys()]

        print(hashes)
        return {"hashes": hashes}

    @app.route("/ipfs/<ipfs_hash>")
    @jinja.template("ipfs_hash.html")  # decorator method is staticmethod
    async def ipfs_hash(request, ipfs_hash):
        if ipfs_hash == "new":
            return {
                "json": app.config["TEMPLATE_PQL_DEFINITION"],
                "hash": "New PQL definition",
            }

        ipfs = ipfshttpclient.connect(app.config["IPFS_API_SERVER_ADDRESS"])

        try:
            js = ipfs.get_json(ipfs_hash, timeout=int(args["--timeout"]))

            return {"json": js, "hash": ipfs_hash}
        except DecodingError:
            return {"error": "Not a JSON file."}
        except:
            return {"error": "Not a file."}

    @app.post("/test_pql")
    async def test_pql_json(request):
        pql = request.json

        try:
            res = await parse_and_execute(pql)
            return response.json({"result": res})
        except Exception as e:
            if hasattr(e, "message"):
                return response.json({"error": e.message})
            else:
                return response.json({"error": str(e)})

    @app.post("/save_pql")
    async def save_pql(request):
        pql = request.json

        try:
            ipfs = ipfshttpclient.connect(app.config["IPFS_API_SERVER_ADDRESS"])
            ipfs_hash = ipfs.add_json(pql)

            return response.json(
                {"success": f"Saving was successful, hash: {ipfs_hash}"}
            )
        except Exception as e:
            return response.json({"error": e.message})

    return app
