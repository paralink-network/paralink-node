import time

from celery import Celery
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session

from src.network.chain import Chain
from src.network.chains import Chains
from src.network.evm_chain import EvmChain
from src.network.substrate_chain import SubstrateChain
from src.process import processor
from src.process.executor import (
    handle_evm_request_event,
    handle_substrate_request_event,
)

logger = get_task_logger(__name__)


def manage_collector(processor: Celery, chain: Chain) -> None:
    """Manage collector to reflect updated chain statuses.

    Args:
        processor (Celery): processor celery application
        chain (Chain): chain to reconcile
    """
    for worker, tasks in processor.control.inspect().active().items():
        for task in tasks:
            if (
                task["name"]
                in [
                    listen_for_evm_events.name,
                    listen_for_substrate_events.name,
                ]
                and task["args"][0]["name"] == chain.name
            ):
                logger.info(
                    f"[[bold]{chain.name}[/]][yellow]Terminate chain collector.[/]"
                )
                processor.control.terminate(task["id"])

    if chain.active:
        if chain.type == "evm":
            logger.info(
                f"[[bold]{chain.name}[/]] Queued [yellow]listening for EVM events[/] task."
            )
            listen_for_evm_events.delay(chain.to_dict())
        elif chain.type == "substrate":
            logger.info(
                f"[[bold]{chain.name}[/]] Queued [yellow]listening for Substrate events[/] task."
            )
            listen_for_substrate_events.delay(chain.to_dict())


async def start_collecting(processor: Celery, chains: Chains, session: Session) -> None:
    """Initiates collecting tasks for addresses specified in the `chains` object."""
    await chains.from_sql(session)
    for chain_name, chain in chains.get_chains():
        manage_collector(processor, chain)


@processor.task
def listen_for_evm_events(chain_payload: dict, poll_interval=2) -> None:
    """listen_for_request_events takes the given contract
    oracle addresses and
    listens for any Request events.

    Args:
        chain_payload: chain payload containing chain information.
        poll_interval: time between the checks.
    """
    while True:
        print(chain_payload["name"])
        time.sleep(20)
    evm_chain = EvmChain(**chain_payload)
    w3 = evm_chain.get_connection()

    event_filters = []
    for contract_address in evm_chain.tracked_contracts:
        contract = w3.eth.contract(
            abi=evm_chain.oracle_metadata, address=contract_address
        )
        filt = contract.events.Request.createFilter(fromBlock="latest")

        logger.info(
            f"[[bold]{evm_chain.name}[/]] Creating filter {filt} for address {contract_address}."
        )
        event_filters.append(filt)

    while True:
        for event_filter in event_filters:
            for event in event_filter.get_new_entries():
                logger.info(
                    f"[[bold]{evm_chain.name}[/]] Request found: {event} with filter {event_filter}."
                )

                handle_evm_request_event.delay(evm_chain, event)

        time.sleep(poll_interval)


@processor.task
def listen_for_substrate_events(chain_payload: dict, poll_interval=2) -> None:
    """listen_for_substrate_events takes the given substrate chain with `tracked_contracts`
    addresses and watches for any `Request` events on the chain.

    Args:
        chain_payload: chain payload containing chain information.
        poll_interval: time between the checks.
    """
    substrate_chain = SubstrateChain(**chain_payload)
    substrate = substrate_chain.get_connection()

    finalised_block_nr = substrate.get_block_number(
        substrate.get_chain_finalised_head()
    )

    # Iterate over every block
    while True:
        block_hash = substrate.get_block_hash(finalised_block_nr)

        # If the block exists, check for any events, otherwise go back to sleep
        if block_hash:
            events = substrate_chain.get_block_events(block_hash)

            for event, decoded_event in events:
                logger.info(
                    f"[[bold]{substrate_chain.name}[/]] Found event {event} | {decoded_event}, block_nr {finalised_block_nr}, "
                )
                handle_substrate_request_event.delay(
                    substrate_chain,
                    decoded_event,
                    {"params": event.params},
                )

            finalised_block_nr += 1
        else:
            time.sleep(poll_interval)
