from abc import ABC, abstractmethod

from src.config import config


class Chain(ABC):
    """Blockchain abstraction for different chains."""

    def __init__(
        self,
        name: str,
        url: str,
        credentials: dict = {},
        active: bool = True,
        tracked_contracts: list = [],
    ):
        """Inits Chain object.

        Args:
            name (str): Name of the chain, should be unique.
            url (str): URL of the chain.
            credentials (dict): a dict of credentials for the chain, differs from chain to
                                chain.
            active (bool): whether the chain is active or inactive
            tracked_contracts (list): list of contracts to listen for events
        """
        self.name = name
        self.url = url
        self.credentials = credentials
        self.tracked_contracts = tracked_contracts
        self.active = active
        if config.VALIDATE_CHAINS:
            self._validate_chain()

    @abstractmethod
    def _validate_chain(self):
        pass
