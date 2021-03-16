import pytest

from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.models.chain import Chain
from src.models.contract import Contract
from src.models.exceptions import ChainNotFound, InvalidAddress


async def test_get_contract(db: Session):
    # Add chain and contract to db
    chain = Chain(active=True, name="eth.mainnet", type="evm")
    contract = Contract(active=False, address="123456789", chain="eth.mainnet")
    db.add_all([chain, contract])
    await db.commit()

    # Assert get_contract fetches correct contract
    fetch = await db.execute(select(Contract))
    result = await Contract.get_contract(db, fetch.scalars().first().id)
    assert result == contract


async def test_get_contracts(db: Session):
    # create multiple chains and multiple contracts
    chain_1 = Chain(active=True, name="eth.mainnet", type="evm")
    chain_2 = Chain(active=True, name="polkadot", type="substrate")
    contract_1 = Contract(active=True, address="add1", chain="eth.mainnet")
    contract_2 = Contract(active=True, address="add2", chain="eth.mainnet")
    contract_3 = Contract(active=True, address="add3", chain="polkadot")
    db.add_all([chain_1, chain_2, contract_1, contract_2, contract_3])
    await db.commit()

    # assert filter on "eth.mainnet" contracts
    eth_mainnet_chains = await Contract.get_contracts(db, "eth.mainnet")
    assert eth_mainnet_chains == [contract_1, contract_2]

    # assert fetch all chains
    all_chains = await Contract.get_contracts(db)
    assert all_chains == [contract_1, contract_2, contract_3]


async def test_create_contract_raises_exceptions_for_invalid_address(db: Session):
    # Test exception raised when chain specified does not exist
    with pytest.raises(ChainNotFound):
        await Contract.create_contract(
            db, address="address", active=True, chain="eth.mainnet"
        )

    # Create chains
    eth_mainnet = Chain(active=True, name="eth.mainnet", type="evm")
    polkadot = Chain(active=True, name="polkadot", type="substrate")
    db.add_all([eth_mainnet, polkadot])
    await db.commit()

    # Check create contract fails on invalid evm address
    with pytest.raises(InvalidAddress):
        await Contract.create_contract(
            db, address="address", active=True, chain="eth.mainnet"
        )

    # Check create contract fails on invalid substrate address
    with pytest.raises(InvalidAddress):
        await Contract.create_contract(
            db, address="address", active=True, chain="polkadot"
        )

    # Check create contract fails on address with wrong ss58 prefix
    kusama_address = "HvnoT6AaxPB9Fry3JH17C8PkoMBZhE73APZx5XJndn24baK"
    with pytest.raises(InvalidAddress):
        await Contract.create_contract(
            db, address=kusama_address, active=True, chain="polkadot"
        )


async def test_create_contract(db: Session):
    # Create chains
    eth_mainnet = Chain(active=True, name="eth.mainnet", type="evm")
    polkadot = Chain(active=True, name="polkadot", type="substrate")
    db.add_all([eth_mainnet, polkadot])
    await db.commit()

    # Create eth contract
    eth_mainnet_contract_address = "0x30293259e3C0034b38E46d464Cf5B0eE652D1d07"
    chain = "eth.mainnet"
    active = True
    await Contract.create_contract(
        db, address=eth_mainnet_contract_address, active=active, chain=chain
    )

    # Fetch eth contract database entry and assert data (ignore autoincrement id)
    result = await db.execute(
        select(Contract).where(
            Contract.address == eth_mainnet_contract_address and Contract.chain == chain
        )
    )
    assert {
        x: y for x, y in result.scalars().first().serialise().items() if x != "id"
    } == {"address": eth_mainnet_contract_address, "active": active, "chain": chain}

    # Check that substrate contract does not error when creating contract with
    # valid polkadot address
    await Contract.create_contract(
        db,
        address="1exaAg2VJRQbyUBAeXcktChCAqjVP9TUxF3zo23R2T6EGdE",
        active=True,
        chain="polkadot",
    )


async def test_set_contract_status(db: Session):
    # Create chain and contract
    chain = Chain(active=True, name="eth.mainnet", type="evm")
    contract = Contract(active=False, chain="eth.mainnet", address="addr1")
    db.add_all([chain, contract])
    await db.commit()

    # Set contract status
    await Contract.set_contract_status(db, contract.id, active=True)

    # Assert contract has been updated in db
    result = await db.execute(select(Contract).where(Contract.id == contract.id))
    assert result.scalars().first().active is True


async def test_delete_contract(db: Session):
    # Create chain and contract
    chain = Chain(active=True, name="eth.mainnet", type="evm")
    contract = Contract(active=False, chain="eth.mainnet", address="addr1")
    db.add_all([chain, contract])
    await db.commit()

    # Delete contract
    await Contract.delete_contract(db, contract.id)

    # Assert contract has been deleted
    result = await db.execute(select(Contract).where(Contract.id == contract.id))
    assert result.scalars().first() is None
