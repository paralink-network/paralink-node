import asyncio

from sanic import Sanic
from sanic_cors import CORS

from src.api import ipfs_bp, pql_bp
from src.api.jsonrpc import init_jsonrpc_endpoints
from src.config import config
from src.logging import DEFAULT_LOGGING_CONFIG
from src.network import chains


def create_app(args={}) -> Sanic:  # noqa: C901
    app = Sanic("src", log_config=DEFAULT_LOGGING_CONFIG)
    app.config.from_object(config)
    app.config.update(args)

    init_jsonrpc_endpoints(app)
    app.blueprint(ipfs_bp)
    app.blueprint(pql_bp)

    CORS(app)

    if app.config["ENABLE_DATABASE"]:
        setup_database(app)

    if app.config["ENABLE_BACKGROUND_WORKER"]:
        from src.process.collector import start_collecting

        asyncio.get_event_loop().run_until_complete(start_collecting(chains))

    return app


def setup_database(app: Sanic):
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    engine = create_async_engine(
        app.config.DATABASE_URL,
        echo=True,
    )

    @app.listener("before_server_start")
    async def connect_to_db(*args, **kwargs):
        app.db = scoped_session(
            sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        )()

    @app.listener("after_server_start")
    async def check_user_signup(*args, **kwargs):
        pass

    @app.listener("after_server_stop")
    async def disconnect_from_db(*args, **kwargs):
        await app.db.close()
