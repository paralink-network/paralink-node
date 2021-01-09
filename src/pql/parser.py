from decimal import Decimal
import asyncio
import typing

import numpy as np

from src.pql.pipeline import Pipeline
from src.pql.exceptions import MethodNotFound
from src.pql.common import to_df, execute_user_query


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
            return await self.aggregate()
        else:
            # Return the result of the last step
            return self.pipelines[-1].step_results[-1]

    async def aggregate(self):
        """Aggregates pipelines results depending on the `method`.
        """
        agg_method = self.pql["aggregate"]["method"]
        pipeline_results = (
            {f"result_{i}": pipeline.step_results[-1] for i, pipeline in enumerate(self.pipelines)}
            if agg_method == "user_query"
            else [Decimal(pipeline.step_results[-1]) for pipeline in self.pipelines]
        )
        print(pipeline_results)
        if agg_method == "mean":
            return np.mean(pipeline_results)
        elif agg_method == "median":
            return np.median(pipeline_results)
        elif agg_method == "max":
            return np.amax(pipeline_results)
        elif agg_method == "min":
            return np.amin(pipeline_results)
        elif agg_method == "user_query":
            parsers = self.pql["aggregate"]["parsers"]
            parsed_results = {
                result_name: to_df(result, parsers[i]) for i, (result_name, result) in enumerate(pipeline_results.items())
            }
            print(parsed_results)
            return await execute_user_query(
                parsed_results,
                self.pql["aggregate"]["query"],
                self.pql["aggregate"]["result"],
            )
        else:
            raise MethodNotFound(f'aggregate method "{agg_method}" not found.',)


async def parse_and_execute(pql: dict) -> typing.Any:
    """parse_and_execute parses the initial PQL version and selects the correct Parser
    class.

    Args:
        pql (dict): a valid PQL JSON

    Returns:
        typing.Any: executed result
    """
    return await Parser(pql).execute()
