from fashionable.unset import UNSET
from jsonschema import ValidationError
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
        self.code = -32003
        self.message = message
        self.data = UNSET


class ParseDataError(Error):
    """ParseDataError is triggered when data can not be parsed."""

    def __init__(self, message: str):
        self.code = -32004
        self.message = message
        self.data = UNSET


class UserQueryError(Error):
    """UserQueryError is triggered when user query fails."""

    def __init__(self, message: str):
        self.code = -32005
        self.message = message
        self.data = UNSET


class PqlValidationError(Error):
    """PqlValidationError is triggered when the Pql fails validation"""

    def __init__(self, message: str):
        self.code = -32006
        self.message = message
        self.data = UNSET


class PqlCustomMethodNotImplementedError(Error):
    """CustomMethodNotImplementedError is trigger when the execute method is not implemented for a custom method"""

    def __init__(self, message: str):
        self.code = -32007
        self.message = message
        self.data = UNSET
