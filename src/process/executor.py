import asyncio
from datetime import datetime

import ipfshttpclient
from celery.utils.log import get_task_logger

from src.config import config
from src.network import chains
from src.network.evm_chain import EvmChain
from src.network.substrate_chain import SubstrateChain
from src.pql.parser import parse_and_execute
from src.utils.ipfs import bytes32_to_ipfs

from . import processor

logger = get_task_logger(__name__)


@processor.task(bind=True)
def handle_evm_request_event(self, evm_chain: EvmChain, event: dict) -> None:
    """Handle Solidity Request function.


    handle_request_event receives a Request Solidity event, executes it and
    writes back to location specified by the callback field.

    Args:
        evm_chain: EvmChain to write the response to
        event: Solidity Request event
    """
    args = event["args"]

    ipfs_hash = bytes32_to_ipfs(args["ipfsHash"])
    expiration = datetime.fromtimestamp(args["expiration"])

    try:
        ipfs = ipfshttpclient.connect(config.IPFS_API_SERVER_ADDRESS)
        req = ipfs.get_json(ipfs_hash, timeout=3)

        logger.debug(f"[{evm_chain.name}] Obtained PQL definition {req}.")

        res = asyncio.run(parse_and_execute(req))
        logger.info(f"[{evm_chain.name}] Obtained result {res}.")

        evm_chain.fulfill(event, res)
    except Exception as e:
        if datetime.now() < expiration:
            self.retry(exc=e)
        else:
            logger.info(
                f"Request {args['requestId']} from {args['requester']} expired due to {str(type(e))}: {e.args[0]}."
            )
            return


@processor.task(bind=True)
def handle_substrate_request_event(
    self,
    substrate_chain: SubstrateChain,
    decoded_event: dict,
    params: dict,
) -> None:
    """Handle Substrate Request function.

    handle_substrate_request_event receives a Request ink! event, executes it and
    writes back to location specified by the callback field.

    Args:
        self: this celery task
        substrate_chain (SubstrateChain): SubstrateChain to write the response to
        decoded_event (dict): decoded SCALE Request event
        params (dict): params of the Request event not provided by the
                       decoded_event, such as external data.
    """
    substrate = substrate_chain.get_connection()

    contract_address = substrate.ss58_encode(params["params"][0]["value"])
    contract = substrate_chain.create_contract_from_address(contract_address)

    # Parse args
    args = {arg["name"]: arg["value"] for arg in decoded_event["args"]}
    ipfs_hash = bytes32_to_ipfs(bytes.fromhex(args["pql_hash"][2:]))

    # Execute IPFS response
    try:
        ipfs = ipfshttpclient.connect(config.IPFS_API_SERVER_ADDRESS)
        req = ipfs.get_json(ipfs_hash, timeout=3)

        logger.debug(f"[{substrate_chain.name}] Obtained PQL definition {req}.")

        res = asyncio.run(parse_and_execute(req))
        logger.info(f"[{substrate_chain.name}] Obtained result {res}.")

        substrate_chain.fulfill(contract, args, res)
    except Exception as e:
        finalised_block_nr = substrate.get_block_number(
            substrate.get_chain_finalised_head()
        )

        if finalised_block_nr < args["valid_till"]:
            self.retry(exc=e)
        else:
            logger.error(
                f"[{substrate_chain.name}] Request {args['request_id']} from {args['from']} expired due to {str(type(e))}: {e.args[0]}"
            )
            return
