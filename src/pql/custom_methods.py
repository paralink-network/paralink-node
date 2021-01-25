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


class MyAdd(CustomMethod):
    PQL_IDENTIFIER = "custom.my_add"
    SCHEMA = {
        "type": "object",
        "properties": {
            "step": {"const": "custom.my_add"},
            "params": {"type": "integer"},
        },
        "required": ["step", "params"],
    }

    @classmethod
    def execute(cls, step: dict, index: int, pipeline) -> typing.Union[float, int]:
        return pipeline.get_value_for_step(index - 1) + step["params"]


# User defined custom methods
PQL_CUSTOM_METHODS = {MyAdd.PQL_IDENTIFIER: MyAdd}
