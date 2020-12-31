import time

from src.process import processor
from src.process.executor import handle_request_event
from src.config import Config
from src.utils import w3


@processor.task
def listen_for_request_events(address: str, poll_interval: int) -> None:
    """listen_for_request_events takes the given contract oracle address and
    listens for any Request events.

    Args:
        address: contract oracle address.
        poll_interval: time between the checks.
    """
    contract = w3.eth.contract(abi=Config.ORACLE_CONTRACT_ABI, address=address)
    event_filter = contract.events.Request.createFilter(fromBlock="latest")

    while True:
        for event in event_filter.get_new_entries():
            handle_request_event.delay(event)
        time.sleep(poll_interval)
