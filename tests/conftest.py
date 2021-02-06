# patch environment
import os

os.environ["VALIDATE_EVM_CHAIN"] = "False"

import pytest  # noqa: E402

from src import create_app  # noqa: E402


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
