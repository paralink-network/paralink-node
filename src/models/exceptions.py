class ActivateChainFailed(Exception):
    """ActiveChainFailed is raised when the Chain could not be activated as it does not
    exist in chain_config.json or it is disabled."""

    pass


class InvalidAddress(Exception):
    """InvalidAddress is raised when the address is not valid for the specified chain."""

    pass


class ChainNotFound(Exception):
    """ChainNotFound is raised when the chain specified is not found."""

    pass
