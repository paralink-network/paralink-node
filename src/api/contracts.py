from sanic import Blueprint, response

from src.models.contract import Contract
from src.network import chains
from src.process import processor
from src.process.collector import manage_collector

contracts_bp = Blueprint("contracts_blueprint", url_prefix="/api/contracts")


@contracts_bp.route("/")
async def get_all_contracts(request) -> response:
    """Get all contracts.

    Args:
        request: request

    Returns:
          response: contracts payload
    """
    contracts = await Contract.get_contracts(request.app.db)
    return response.json(
        {"contracts": [contract.serialise() for contract in contracts]}
    )


@contracts_bp.route("/<chain>")
async def get_chain_contracts(request, chain: str) -> response:
    """Get contracts for specified chain.

    Args:
        request: request
        chain: chain name

    Returns:
        response: contracts payload
    """
    contracts = await Contract.get_contracts(request.app.db, chain)
    return response.json(
        {"contracts": [contract.serialise() for contract in contracts]}
    )


@contracts_bp.post("/")
async def create_contract(request) -> response:
    """Create contract.

    Args:
        request: request

    Returns:
        response: response
    """
    data = request.json
    await Contract.create_contract(
        request.app.db, data["address"], data["active"], data["chain"]
    )

    if request.app.config["ENABLE_BACKGROUND_WORKER"]:
        await chains.from_sql(request.app.db)
        manage_collector(processor, chains.get_chain(data["chain"]))
    return response.json({"result": "ok"})


@contracts_bp.put("<id>")
async def set_contract_status(request, id: str) -> response:
    """Set contract status.

    Args:
        request: request
        id: contract id

    Returns:
        response: response
    """
    data = request.json
    await Contract.set_contract_status(request.app.db, id, data["active"])

    if request.app.config["ENABLE_BACKGROUND_WORKER"]:
        await chains.from_sql(request.app.db)
        manage_collector(
            processor, (await Contract.get_contract(request.app.db, id)).chain
        )

    return response.json({"result": "ok"})


@contracts_bp.delete("<id>")
async def delete_contract(request, id: str):
    """Delete contract.

    Args:
        request: request
        id: contract id

    Returns:
        response: response
    """
    await Contract.delete_contract(request.app.db, id)

    if request.app.config["ENABLE_BACKGROUND_WORKER"]:
        await chains.from_sql(request.app.db)
        manage_collector(
            processor, (await Contract.get_contract(request.app.db, id)).chain
        )

    return response.json({"result": "ok"})
