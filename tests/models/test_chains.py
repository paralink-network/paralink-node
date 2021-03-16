import pytest

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.models.chain import Chain
from src.models.exceptions import ActivateChainFailed


async def test_get_chain(db: Session):
    # Create test chain in db
    chain = Chain(name="chain_1", type="evm", active=True)
    db.add(chain)
    await db.commit()

    # Fetch and assert chain
    result = await Chain.get_chain(db, "chain_1")
    assert chain == result


async def test_get_chains(db: Session):
    # Crate multiple test chains in db
    chain_1 = Chain(name="chain_1", type="evm", active=True)
    chain_2 = Chain(name="chain_2", type="substrate", active=True)
    db.add_all([chain_1, chain_2])
    await db.commit()

    # Fetch and assert chains
    result = await Chain.get_chains(db)
    assert result == [chain_1, chain_2]


async def test_reconcile_chains(db, chains):
    # Create multiple test chains in db
    chain_1 = Chain(name="chain_1", type="evm", active=True)
    chain_2 = Chain(name="chain_2", type="substrate", active=True)
    db.add_all([chain_1, chain_2])
    await db.commit()

    # execute reconciliation method and fetch result
    chains = await Chain.reconcile_chains(db, chains)
    result = await db.execute(select(Chain))
    result = result.scalars().all()

    # Create list of Chain models for Chain's in  Chains object
    chains_models = [
        Chain(name=chain.name, type=chain.type, active=chain.active)
        for _, chain in chains.get_chains().items()
    ]

    # Assert that expected chain entries in db
    assert sorted([x.serialise() for x in result], key=lambda x: x["name"]) == sorted(
        [x.serialise() for x in [chain_1, chain_2] + chains_models],
        key=lambda x: x["name"],
    )

    # Assert that chain not in chains object has been disabled
    assert (
        await db.execute(select(Chain).where(Chain.name == "chain_1"))
    ).scalars().first().active is False


async def test_set_chain_status_on_chain_not_in_config(db: Session, chains):
    # Add chain that doesn't exist in chain_config.json
    chain_1 = Chain(name="test.chain", type="evm", active=False)
    db.add(chain_1)
    await db.commit()

    # Assert exception is raised when attempt made to activate chain that doesn't exist
    # in chain_config.json
    with pytest.raises(ActivateChainFailed):
        await Chain.set_chain_status(db, "test.chain", active=True, chains=chains)


async def test_set_chain_status(db: Session, chains):
    # Add chain to database
    chain_1 = Chain(name="eth.mainnet", type="evm", active=False)
    db.add(chain_1)
    await db.commit()

    # Change chain status and assert updated value
    await Chain.set_chain_status(db, "eth.mainnet", active=True, chains=chains)
    result = await db.execute(select(Chain).where(Chain.name == "eth.mainnet"))
    assert result.scalars().first().active is True
