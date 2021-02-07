import json
from importlib import import_module
from os import getenv
from pathlib import Path

import yaml
from dotenv import load_dotenv

__version__ = "0.1.0"

# Load the main configuration file
load_dotenv(".env")


def parse_and_import_custom_methods(plugins_config_path: Path) -> dict:
    """Helper function to parse specified custom methods and import the classes from the required modules.

    Args:
        plugins_config_path (Path): path to plugins config file which contains a list of custom methods.
        Each string element in the list corresponds to a custom method and is specified using the pattern module:class.

    Returns:
        A dict with the custom method PQL identifier as the key and the custom method
        class as the value.

    """
    plugins_config = yaml.safe_load(open(str(plugins_config_path.absolute()), "r"))
    import_specs = [
        {"module": plugin.split(":")[0], "class": plugin.split(":")[1]}
        for plugin in plugins_config["plugins"]
    ]
    return {
        custom_method.PQL_IDENTIFIER: custom_method
        for custom_method in [
            getattr(import_module(import_spec["module"]), import_spec["class"])
            for import_spec in import_specs
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

    # Database
    DB_DATABASE = getenv("DATABASE_NAME", "paralink_node")
    DB_HOST = getenv("DATABASE_HOST", "localhost")
    DB_USER = getenv("DATABASE_USER", "paralink")
    DB_PASSWORD = getenv("DATABASE_PASSWORD", "p4r4link")
    DATABASE_URL = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"

    # Whether to start a background worker that will collect events from chains
    ENABLE_BACKGROUND_WORKER = getenv("ENABLE_BACKGROUND_WORKER", "True") == "True"
    ENABLE_DATABASE = getenv("ENABLE_DATABASE", "True") == "True"

    # Default number of confirmations for ETH finality
    DEFAULT_NUM_CONFIRMATIONS = 40

    # Node data folder
    DATA_FOLDER = Path.home().joinpath(".paralink")
    Path(DATA_FOLDER).mkdir(exist_ok=True)
    ETHEREUM_KEYSTORE_PATH = getenv(
        "ETHEREUM_KEYSTORE_PATH", DATA_FOLDER.joinpath("ethkey.json")
    )

    # Use ETH keystore password directly from the env variable
    USE_ENV_VARIABLE_FOR_ETHEREUM_KEYSTORE = (
        getenv("USE_ENV_VARIABLE_FOR_ETHEREUM_KEYSTORE", "False") == "True"
    )
    # Only used if above is True
    ETHEREUM_KEYSTORE_PASSWORD = getenv("ETHEREUM_KEYSTORE_PASSWORD", "paralink")

    TEMPLATE_PQL_DEFINITION = json.load(
        open("src/data/default_pql_template_definition.json")
    )
    ORACLE_CONTRACT_ABI = json.load(open("src/data/oracle_abi.json"))

    # Plugins config path
    PLUGINS_CONFIG_PATH = Path(DATA_FOLDER).joinpath("plugins.yaml")

    # Create default plugins config if it doesn't exist
    if not PLUGINS_CONFIG_PATH.exists():
        plugins_config = yaml.safe_load(open("src/data/default_plugins.yaml", "r"))
        yaml.safe_dump(plugins_config, open(PLUGINS_CONFIG_PATH.absolute(), "w"))

    PQL_CUSTOM_METHODS = parse_and_import_custom_methods(PLUGINS_CONFIG_PATH)

    def __init__(self):
        # Create default chain config if it doesn't exist
        chain_config = Path(self.DATA_FOLDER).joinpath("chain_config.json")
        if not chain_config.exists():
            chains_json = json.load(open("src/data/default_chain_config.json", "r"))
            chains_json[0]["url"] = self.WEB3_PROVIDER_URI
            json.dump(chains_json, open(chain_config.absolute(), "w"))


config = Config()
