import typing
from abc import abstractmethod

from src.pql.exceptions import PqlCustomMethodNotImplementedError


class CustomMethod:
    """Abstract class that defines the interface for custom methods.

    All custom methods must have three core components, a pql identifier, a schema and
    an execute method which defines the transformational logic.

    Attributes:
        PQL_IDENTIFIER: the identifier used to reference the custom method from PQL.
        SCHEMA: the schema the step must adhered to such that all custom method dependencies are satisfied.
    """

    PQL_IDENTIFIER: str
    SCHEMA: dict

    @classmethod
    @abstractmethod
    def execute(cls, step: dict, index: int, pipeline) -> typing.Any:
        """Abstract method that contains the transformational logic.

        Args:
            step: step PQL json.
            index: index of the step.
            pipeline: The pipeline that the method is being execute on.

        Returns:
            The result of the custom methods logic.

        Raises:
            PqlCustomMethodNotImplementedError: The subclass has not implemented the execute method.
        """
        raise PqlCustomMethodNotImplementedError(
            f"Custom method not implemented for {cls.PQL_IDENTIFIER}"
        )
