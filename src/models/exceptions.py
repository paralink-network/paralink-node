class ActivateChainFailed(Exception):
    """ActiveChainFailed is raised when the Chain could not be activated as it does not
    exist in chain_config.json or it is disabled."""

    pass
