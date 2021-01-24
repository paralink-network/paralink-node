import json
from importlib import import_module
from os import getenv
from pathlib import Path

from dotenv import load_dotenv

from src.pql.custom_methods.my_add import MyAdd
from src.pql.custom_methods.sklearn import Sklearn

__version__ = "0.1.0"

# Load the main configuration file
load_dotenv(".env")


def parse_and_import_custom_methods(import_specs: list) -> dict:
    return {
        custom_method.PQL_IDENTIFIER: custom_method
        for custom_method in [
            getattr(import_module(import_spec[0]), import_spec[1])
            for import_spec in [import_spec.split(":") for import_spec in import_specs]
        ]
    }


class Config:
    DEBUG = getenv("DEBUG", "False") == "True"
    TESTING = getenv("TESTING", "False") == "True"

    # Ethereum
    ETHERSCAN_KEY = getenv("ETHERSCAN_KEY")
    GETH_HTTP_RPC = getenv("GETH_HTTP_RPC", "http://localhost:8745")
    IPFS_API_SERVER_ADDRESS = getenv("IPFS_API_SERVER_ADDRESS")
    WEB3_PROVIDER_URI = getenv("WEB3_PROVIDER_URI")

    CELERY_BROKER_URL = getenv("CELERY_BROKER_URL")
    DATABASE_URL = getenv("DATABASE_URL")

    # Whether to start a background worker that will collect events from chains
    ENABLE_BACKGROUND_WORKER = getenv("ENABLE_BACKGROUND_WORKER", "True") == "True"

    # Default number of confirmations for ETH finality
    DEFAULT_NUM_CONFIRMATIONS = 40

    # Node data folder
    DATA_FOLDER = Path.home().joinpath(".paralink")
    ETHEREUM_KEYSTORE_PATH = getenv(
        "ETHEREUM_KEYSTORE_PATH", DATA_FOLDER.joinpath("ethkey.json")
    )

    # Use ETH keystore password directly from the env variable
    USE_ENV_VARIABLE_FOR_ETHEREUM_KEYSTORE = (
        getenv("USE_ENV_VARIABLE_FOR_ETHEREUM_KEYSTORE", "False") == "True"
    )
    # Only used if above is True
    ETHEREUM_KEYSTORE_PASSWORD = getenv("ETHEREUM_KEYSTORE_PASSWORD", "paralink")

    TEMPLATE_PQL_DEFINITION = json.load(open("src/data/oracle_abi.json"))
    ORACLE_CONTRACT_ABI = json.load(open("src/data/oracle_abi.json"))

    # User defined custom methods
    PQL_CUSTOM_METHODS_IMPORTS = [
        "src.pql.custom_methods.my_add:MyAdd",
        "src.pql.custom_methods.sklearn:Sklearn",
    ]
    PQL_CUSTOM_METHODS = parse_and_import_custom_methods(PQL_CUSTOM_METHODS_IMPORTS)

    def __init__(self):
        Path(self.DATA_FOLDER).mkdir(exist_ok=True)


config = Config()
