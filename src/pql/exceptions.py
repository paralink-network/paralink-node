from typing import Any

from fashionable.unset import UNSET
from sanic_jsonrpc.errors import Error


class PqlDecodingError(Error):
    """PqlDecodingError is triggered when given PQL definition cannot be decoded (this includes incorrect format as well as
    empty PQL definition - in case it is not found).
    """

    def __init__(self, message: str):
        self.code = -32001
        self.message = message
        self.data = UNSET


class ExternalError(Error):
    """ExternalError is triggered when there is an issue with external dependency (such as IPFS, ETH node)."""

    def __init__(self, message: str):
        self.code = -32002
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


class StepNotFound(Error):
    """StepNotFound is triggered when step is not found."""

    def __init__(self, message: str):
        self.code = -32010
        self.message = message
        self.data = UNSET


class MethodNotFound(Error):
    """MethodNotFound is triggered when pipeline method is not found."""

    def __init__(self, message: str):
        self.code = -32011
        self.message = message
        self.data = UNSET


class ArgumentError(Error):
    """ArgumentError is triggered when PQL arguments are incorrect."""

    def __init__(self, message: str):
        self.code = -32012
        self.message = message
        self.data = UNSET


class ParserNotFound(Error):
    """UserQueryError is triggered when user query fails.
    """

    def __init__(self, message: str):
        self.code = -32013
        self.message = message
        self.data = UNSET


class ParseDataError(Error):
    """ParseDataError is triggered when data can not be parsed.
    """

    def __init__(self, message: str):
        self.code = -32014
        self.message = message
        self.data = UNSET


class UserQueryError(Error):
    """UserQueryError is triggered when user query fails.
    """

    def __init__(self, message: str):
        self.code = -32015
        self.message = message
        self.data = UNSET
