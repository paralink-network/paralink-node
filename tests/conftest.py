from os import getenv

import pytest

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src import create_app
from src.models import Base
from src.network.chains import Chains


@pytest.fixture(scope="session")
def app():
    args = {
        "ENABLE_DATABASE": False,
        "ENABLE_BACKGROUND_WORKER": False,
    }
    app = create_app(args)
    yield app


@pytest.fixture
def client(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


@pytest.fixture(scope="session")
def engine():
    # Test Database
    TEST_DATABASE_NAME = getenv("TEST_DATABASE_NAME", "test_database")
    TEST_DATABASE_HOST = getenv("TEST_DATABASE_HOST", "test_psql")
    TEST_DATABASE_USER = getenv("TEST_DATABASE_USER", "test_user")
    TEST_DATABASE_PASSWORD = getenv("TEST_DATABASE_PASSWORD", "test_password")
    TEST_DATABASE_URL = f"postgresql://{TEST_DATABASE_USER}:{TEST_DATABASE_PASSWORD}@{TEST_DATABASE_HOST}/{TEST_DATABASE_NAME}"
    return create_async_engine(TEST_DATABASE_URL)


@pytest.fixture()
async def tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture()
async def db(engine, tables):
    async with engine.connect() as conn:
        # Create transaction scope
        transaction = await conn.begin()
        session = sessionmaker(expire_on_commit=False, bind=conn, class_=AsyncSession)()

        yield session

        # Clean up
        await session.close()
        await transaction.rollback()


@pytest.fixture()
def chains():
    chain_config = [
        {
            "name": "eth.mainnet",
            "type": "evm",
            "project": "eth",
            "url": "https://mainnet.infura.io/v3/<infura-project-id>",
            "credentials": {},
            "enabled": True,
            "tracked_contracts": [],
        }
    ]
    return Chains.from_list(chain_config)
