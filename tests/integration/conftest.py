import pytest
from src import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app(None)
    yield app


@pytest.fixture
def client(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))
