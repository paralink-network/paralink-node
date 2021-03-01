import asyncio

from sanic import Sanic
from sanic.log import logger
from sanic_cors import CORS

from src.api import chains_bp, contracts_bp, ipfs_bp, pql_bp
from src.api.jsonrpc import init_jsonrpc_endpoints
from src.config import config
from src.logging import DEFAULT_LOGGING_CONFIG
from src.models.chain import Chain
from src.models.contract import Contract
from src.network import chains


def create_app(args: dict = {}) -> Sanic:  # noqa: C901
    """Creates Sanic app with all dependencies.

    Args:
        args (dict): CLI arguments dict.

    Returns:
        Sanic: Sanic app
    """
    app = Sanic("src", log_config=DEFAULT_LOGGING_CONFIG)
    app.config.from_object(config)
    app.config.update(args)

    init_jsonrpc_endpoints(app)
    app.blueprint(ipfs_bp)
    app.blueprint(pql_bp)
    app.blueprint(chains_bp)
    app.blueprint(contracts_bp)

    CORS(app)

    if app.config["ENABLE_DATABASE"]:
        setup_database(app)

    if app.config["ENABLE_BACKGROUND_WORKER"]:
        from src.process.collector import start_collecting

        @app.listener("after_server_start")
        async def start_processor(*args, **kwargs):
            await start_collecting(chains, app.db)

    return app


def setup_database(app: Sanic):
    """Initalizes DB session.

    Args:
        app (Sanic): Sanic app
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(app.config.DATABASE_URL)

    @app.listener("before_server_start")
    async def connect_to_db(*args, **kwargs):
        """Initalizes DB before server starts."""
        app.db = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)()

    @app.listener("after_server_start")
    async def check_user_signup(*args, **kwargs):
        """Checks whether user is present in the DB."""
        from src.cli.utils.user_prompt import user_prompt
        from src.models.user import User

        # Check for existing user
        user = await User.get_user(app)

        if not user:
            # User was not found, we have to create it
            logger.info("No existing user found. A new user will be created.")

            username, password = user_prompt()

            logger.info(f"Creating new user [magenta bold]{username}[/].")
            user = await User.create_user(app, username, password)
        else:
            logger.info(f"Existing user [magenta bold]{user.username}[/] found.")

    @app.listener("after_server_start")
    async def reconcile_chains(*args, **kwargs):
        """Reconciles chain data in chain_config.json with database."""
        await Chain.reconcile_chains(app.db, chains)

    @app.listener("after_server_stop")
    async def disconnect_from_db(*args, **kwargs):
        """Closes DB connection after server stops."""
        await app.db.close()
