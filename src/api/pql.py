import ipfshttpclient
from ipfshttpclient.exceptions import DecodingError
from sanic import Blueprint, response

from src.pql.parser import parse_and_execute

pql_bp = Blueprint("pql_blueprint", url_prefix="/api/pql")


@pql_bp.post("/test")
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
