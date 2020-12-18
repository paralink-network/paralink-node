import asyncio
import typing

from .pipeline import Pipeline


class Parser:
    """PQL parser accepts a PQL dict object, parses the definition and executes the defined
    steps.
    """

    def __init__(self, pql: dict):
        """Inits Parser.

        Args:
            pql (dict): a valid PQL dict object
        """
        self.pql = pql
        self.pipelines = []

    async def execute(self) -> typing.Any:
        """Executes given PQL dict object.

        Returns:
            typing.Any: an object produced by the last step of pipeline or as a result of
            aggregation of multiple pipelines.
        """
        # Execute pipelines
        self.pipelines = [
            Pipeline(pipeline_pql) for pipeline_pql in self.pql["sources"]
        ]

        await asyncio.gather(*[pipeline.execute() for pipeline in self.pipelines])

        # Aggregate stage
        if "aggregate" in self.pql:
            return self.aggregate()
        else:
            # Return the result of the last step
            return self.pipelines[-1].step_results[-1]

    async def aggregate(self):
        pass

