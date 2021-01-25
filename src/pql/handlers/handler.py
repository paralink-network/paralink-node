import typing


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
