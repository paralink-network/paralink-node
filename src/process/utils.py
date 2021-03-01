from celery import Celery
from sqlalchemy.orm import Session

from src.network.chains import Chains
from src.process.collector import (
    listen_for_evm_events,
    listen_for_substrate_events,
    start_collecting,
)


async def restart_collectors(
    processor: Celery, chains: Chains, session: Session
) -> None:
    """Restart collectors to reflect updated chain statuses.

    Args:
        processor (Celery): processor celery application
        chains (Chains): Chains object containing chain data
        session (Session): sqlalchemy session
    """
    for worker, tasks in processor.control.inspect().active().items():
        for task in tasks:
            if task["name"] in [
                listen_for_evm_events.name,
                listen_for_substrate_events.name,
            ]:
                processor.control.terminate(task["id"])
    await start_collecting(chains, session)
