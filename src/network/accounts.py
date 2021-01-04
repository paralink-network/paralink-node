# from getpass import getpass
import stdiomask
import json
import logging
from pathlib import Path

from src.config import config
from src.network.web3 import w3

logger = logging.getLogger(__name__)


class Accounts:
    """Accounts manages node accounts on different chains.
    """

    def __init__(self):
        self.ethkey = None

    def load(self):
        """Load private keys from the env variables. Creates a new account if private key
        does not exist.
        """
        eth_json = Path(config.ETHEREUM_KEYSTORE_PATH)
        logger.info(f"Loading ETH private key from {eth_json}")

        if eth_json.exists():
            password = self.get_password(f"Enter the password for {eth_json} ")
            with eth_json.open() as fp:
                private_key = w3.eth.account.decrypt(json.load(fp), password)
                self.ethkey = w3.eth.account.from_key(private_key)
        else:
            logger.info(f"Private key not found. A new one will be created.")
            self.ethkey = w3.eth.account.create()
            self.save(self.ethkey)

        logger.info(f"Using ETH address: {self.ethkey.address}")

    def save(self, ethkey):
        """Save given LocalACcount to ETH keystore.

        Args:
            ethkey: eth_account.LocalAccount
        """
        eth_json = Path(config.ETHEREUM_KEYSTORE_PATH)

        password = self.get_password(
            f"Enter the password to encrypt new ETH private key {eth_json}: ",
        )
        encrypted = w3.eth.account.encrypt(ethkey.privateKey, password)

        # Write back the newly generate private key
        with eth_json.open("w") as fp:
            json.dump(encrypted, fp)
            logger.info(f"{eth_json} was created and encrypted.")

    def import_key(self, private_key: str):
        """Imports given private_key into ETH keystore.

        Args:
            private_key: private key to be imported.
        """
        self.ethkey = w3.eth.account.from_key(private_key)
        self.save(self.ethkey)

        logger.info(f"Successfully imported key {self.ethkey.address}")

    def get_password(self, message) -> str:
        """Prompts user for password (hidden input).

        Args:
            message: Message to be displayed before prompt.
        """
        if config.USE_ENV_VARIABLE_FOR_ETHEREUM_KEYSTORE:
            return config.ETHEREUM_KEYSTORE_PASSWORD
        else:
            return stdiomask.getpass(message)
