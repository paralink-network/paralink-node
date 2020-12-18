import typing


class Handler:
    """ Interface for implementing different handlers.
    """

    async def execute(self, pql) -> typing.Any:
        pass
