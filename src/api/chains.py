from sanic import Blueprint, response
from sanic.exceptions import NotFound

from src.models.chain import Chain
from src.models.exceptions import ActiveChainFailed
from src.process.utils import restart_collectors

chains_bp = Blueprint("chains_blueprint", url_prefix="/api/chains")


@chains_bp.route("/")
async def get_chains(request) -> response:
    """Get all chains.

    Args:
        request: request

    Returns:
        response: chains payload
    """
    chains = await Chain.get_chains(request.app.db)
    return response.json({"chains": [chain.serialise() for chain in chains]})


@chains_bp.route("/<chain>")
async def get_chain(request, chain: str) -> response:
    """Get chain.

    Args:
        request: request
        chain: chain name

    Returns:
        response: chain payload
    """
    chain = await Chain.get_chain(request.app.db, chain)
    return response.json({"chain": chain.serialise()})


@chains_bp.put("/<chain>")
async def set_chain_status(request, chain: str) -> response:
    """Set the chain status.

    Args:
        request: request
        chain: chain name

    Returns:
        response: response
    """
    from src.network import chains
    from src.process import processor

    try:
        await Chain.set_chain_status(request.app.db, chain, request.json.get("active"))
    except ActiveChainFailed as e:
        raise NotFound(e)

    await restart_collectors(processor, chains, request.app.db)
    return response.json({"result": "ok"})
