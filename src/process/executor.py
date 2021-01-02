import asyncio
from datetime import datetime

from celery.utils.log import get_task_logger
import ipfshttpclient

from . import processor
from src.config import config
from src.network.web3 import w3

from src.pql.parser import parse_and_execute
from src.utils.ipfs import bytes32_to_ipfs

logger = get_task_logger(__name__)


@processor.task(bind=True)
def handle_request_event(self, event) -> None:
    """handle_request_event receives a Request Solidity event, executes it and
    writes back to location specified by the callback field.

    Args:
        event: Solidity Request event
    """
    print(event)
    args = event["args"]

    ipfs_hash = bytes32_to_ipfs(args["ipfsHash"])
    expiration = datetime.fromtimestamp(args["expiration"])

    try:
        ipfs = ipfshttpclient.connect(config.IPFS_API_SERVER_ADDRESS)
        req = ipfs.get_json(ipfs_hash, timeout=3)

        logger.debug(f"Obtained PQL definition {req}")

        res = asyncio.run(parse_and_execute(req))
        logger.info(f"Obtained result {res}")

        # TODO: use callback
        print(f"Writing {res} to callback")
    except Exception as e:
        if datetime.now() < expiration:
            self.retry(exc=e)
        else:
            logger.info(
                f"Request {args['requestId']} from {args['requester']} expired due to {str(type(e))}: {e.args[0]}"
            )
            return
