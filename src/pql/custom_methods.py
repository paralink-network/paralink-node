import typing


class MyAdd:
    PQL_IDENTIFIER = "custom.my_add"
    SCHEMA = {
        "type": "object",
        "properties": {
            "step": {"const": "custom.my_add"},
            "params": {"type": "integer"},
        },
        "required": ["step", "params"],
    }

    @staticmethod
    def execute(step: dict, index: int, pipeline) -> typing.Union[float, int]:
        return pipeline.get_value_for_step(index - 1) + step["params"]


# User defined custom functions
PQL_CUSTOM_METHODS = {MyAdd.PQL_IDENTIFIER: MyAdd}
