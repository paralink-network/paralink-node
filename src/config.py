from os import getenv
from dotenv import load_dotenv

from src.pql.handlers.rest_api_handler import RestApiHandler

__version__ = "0.1.0"

# Load the main configuration file
load_dotenv(".env")


class Config:
    DEBUG = False
    TESTING = False

    # Ethereum
    ETHERSCAN_KEY = getenv("ETHERSCAN_KEY")
    GETH_HTTP_RPC = getenv("GETH_HTTP_RPC", "http://localhost:8745")
    IPFS_API_SERVER_ADDRESS = getenv("IPFS_API_SERVER_ADDRESS")
    WEB3_PROVIDER_URI = getenv("WEB3_PROVIDER_URI")

    DATABASE_URL = getenv("DATABASE_URL")

    # Default number of confirmations for ETH finality
    DEFAULT_NUM_CONFIRMATIONS = 40

    TEMPLATE_PQL_DEFINITION = {
        "name": "My job name",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Pipeline 1 name",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://my-crypto-api.com/tickers",
                    },
                ],
            },
            {
                "name": "Pipeline 2 name",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://my-crypto-api.com/tickers",
                    },
                ],
            },
        ],
        "aggregate": {"method": "mean"},
        "callback": [
            {
                "type": "chain.eth",
                "params": {
                    "address": "<ORACLE ETH ADDRESS>",
                    "function": "fulfillRequest",
                    "args": [],
                },
            },
            {
                "type": "chain.plasm",
                "params": {
                    "address": "<ORACLE PLASM ADDRESS>",
                    "function": "fulfillRequest",
                    "args": [],
                },
            },
        ],
    }

    # User defined custom functions
    PQL_CUSTOM_METHODS = {
        # "my_add": lambda step, index, pipeline: pipeline.get_value_for_step(index - 1) + step["params"]
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
