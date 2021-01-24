import typing

from src.pql.custom_methods import CustomMethod


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
