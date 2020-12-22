from os import getenv
from dotenv import load_dotenv

from src.pql.handlers.rest_api_handler import RestApiHandler

# Load the main configuration file
load_dotenv(".env")

# Ethereum
ETHERSCAN_KEY = getenv("ETHERSCAN_KEY")
INFURA_KEY = getenv("INFURA_KEY")
GETH_HTTP_RPC = getenv("GETH_HTTP_RPC", "http://localhost:8745")


class Config:
    DEBUG = False
    TESTING = False

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
