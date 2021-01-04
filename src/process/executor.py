import asyncio
from datetime import datetime

from celery.utils.log import get_task_logger
import ipfshttpclient

from . import processor
from src.config import config
from src.network.web3 import w3

from src.pql.parser import parse_and_execute
from src.utils.ipfs import bytes32_to_ipfs
from src.network import accounts

logger = get_task_logger(__name__)


@processor.task(bind=True)
def handle_request_event(self, event) -> None:
    """handle_request_event receives a Request Solidity event, executes it and
    writes back to location specified by the callback field.

    Args:
        event: Solidity Request event
    """
    args = event["args"]

    ipfs_hash = bytes32_to_ipfs(args["ipfsHash"])
    expiration = datetime.fromtimestamp(args["expiration"])

    try:
        ipfs = ipfshttpclient.connect(config.IPFS_API_SERVER_ADDRESS)
        req = ipfs.get_json(ipfs_hash, timeout=3)

        logger.debug(f"Obtained PQL definition {req}")

        res = asyncio.run(parse_and_execute(req))
        logger.info(f"Obtained result {res}")

        write_to_eth_chain(event, res)
    except Exception as e:
        if datetime.now() < expiration:
            self.retry(exc=e)
        else:
            logger.info(
                f"Request {args['requestId']} from {args['requester']} expired due to {str(type(e))}: {e.args[0]}"
            )
            return


def write_to_eth_chain(event, res):
    """It writes `res` (result of the PQL definition) to the location specified in the `Request` event.

    Args:
        event: a Request event from ETH chain.
        res: already executed PQL definition
    """
    logger.info(f"Writing {res} to ETH chain")

    args = event["args"]
    contract = w3.eth.contract(abi=config.ORACLE_CONTRACT_ABI, address=event["address"])

    tx = contract.functions.fulfillRequest(
        args["requestId"],
        args["callbackAddress"],
        args["callbackFunctionId"],
        args["expiration"],
        w3.toBytes(int(res)).rjust(32, b"\0"),
    ).buildTransaction()

    tx.update({"nonce": w3.eth.getTransactionCount(accounts.ethkey.address)})

    signed_tx = w3.eth.account.signTransaction(tx, accounts.ethkey.privateKey)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    logger.info(tx_receipt)
