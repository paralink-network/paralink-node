import typing
from abc import abstractmethod

from src.pql.exceptions import PqlCustomMethodNotImplementedError


class CustomMethod:
    PQL_IDENTIFIER: str
    SCHEMA: dict

    @classmethod
    @abstractmethod
    def execute(cls, step: dict, index: int, pipeline) -> typing.Any:
        raise PqlCustomMethodNotImplementedError(
            f"Custom method not implemented for {cls.PQL_IDENTIFIER}"
        )
