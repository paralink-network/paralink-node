import typing

from src.pql.exceptions import ArgumentError


class Handler:
    """Interface for implementing different handlers."""

    @staticmethod
    async def execute(pql: dict) -> typing.Any:
        """Execute given PQL JSON

        Args:
            pql (dict): PQL JSON

        Returns:
            typing.Any: result of the execution of PQL JSON
        """
        pass

    @staticmethod
    def require_params(step: dict, param_list: typing.List) -> None:
        """Checks whether all params in `param_list` are present in the given `step` dict.
        Raises and ArgumentError exception if it is not present.

        Args:
            step (dict): step
            param_list (typing.List): param_list

        Raises:
            ArgumentError: a param in param_list is not present.

        Returns:
            None:
        """
        for param in param_list:
            if param not in step:
                raise ArgumentError(f"Parameter {param} is required in {step}")
