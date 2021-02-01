import typing

from src.pql.custom_methods import CustomMethod


class MyAdd(CustomMethod):
    """A custom method class which enables addition functionality within PQL.

    Attributes:
        PQL_IDENTIFIER: the identifier used to reference the MyAdd method from PQL.
        SCHEMA: the schema the step must adhere to such that all MyAdd dependencies are satisfied.
    """

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
        """Contains the logic to add a specified value to the last step of the pipeline.

        Args:
            step: step PQL json.
            index: index of the step.
            pipeline: The pipeline that the method is being executed on.

        Returns:
            the sum of the previous step of the pipeline and the value specified in step["params"].
        """
        return pipeline.get_value_for_step(index - 1) + step["params"]
