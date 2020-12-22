from typing import Any

from fashionable.unset import UNSET
from sanic_jsonrpc.errors import Error


class MethodNotFound(Error):
    """MethodNotFound is triggered when pipeline method is not found.
    """

    def __init__(self, message: str):
        self.code = -32010
        self.message = message
        self.data = UNSET


class NoInputValue(Error):
    """NoInputValue is triggered when there is not value from the previous step to act
    upon.
    """

    def __init__(self, message: str):
        self.code = -32009
        self.message = message
        self.data = UNSET
