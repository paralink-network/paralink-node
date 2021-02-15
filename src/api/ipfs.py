import ipfshttpclient
from ipfshttpclient.exceptions import DecodingError
from sanic import Blueprint, response

ipfs_bp = Blueprint("ipfs_blueprint", url_prefix="/api/ipfs")


@ipfs_bp.route("/")
async def list(request):
    """Lists local IPFS hashes.

    Args:
        request: request
    """
    # Connect to the IPFS API server
    ipfs = ipfshttpclient.connect(request.app.config["IPFS_API_SERVER_ADDRESS"])
    hashes = [key for key in ipfs.pin.ls(type="recursive")["Keys"].keys()]

    return response.json({"hashes": hashes})


@ipfs_bp.route("/<ipfs_hash>")
async def api_ipfs_hash(request, ipfs_hash: str):
    """Get PQL contents in `ipfs_hash`, return error if not valid PQL.

    Args:
        ipfs_hash: PQL JSON
    """
    if ipfs_hash == "new":
        return response.json(
            {
                "pql": request.app.config["TEMPLATE_PQL_DEFINITION"],
                "hash": "New PQL definition",
            }
        )

    ipfs = ipfshttpclient.connect(request.app.config["IPFS_API_SERVER_ADDRESS"])

    try:
        js = ipfs.get_json(ipfs_hash, timeout=int(request.app.config["--timeout"]))

        return response.json({"pql": js, "hash": ipfs_hash})
    except DecodingError:
        return response.json({"error": "Not a JSON file."}, status=400)
    except Exception:
        return response.json({"error": "Not a file."}, status=400)


@ipfs_bp.post("/save_pql")
async def save_pql(request):
    """Saves given JSON `request` and returns successful JSON.

    Args:
        request: PQL JSON
    """
    pql = request.json

    try:
        ipfs = ipfshttpclient.connect(request.app.config["IPFS_API_SERVER_ADDRESS"])
        ipfs_hash = ipfs.add_json(pql)

        return response.json({"success": f"Saving was successful, hash: {ipfs_hash}"})
    except Exception as e:
        return response.json({"error": e.message})
