import asyncio
import typing
from decimal import Decimal

import numpy as np
from jsonschema import ValidationError, validate

from src.pql.exceptions import MethodNotFound, PqlValidationError
from src.pql.pipeline import Pipeline
from src.pql.query_sql import construct_aggregate_sql_payload, execute_sql_query
from src.pql.schema import pql as pql_schema


class Parser:
    """PQL parser accepts a PQL dict object, parses the definition and executes the defined
    steps.
    """

    def __init__(self, pql: dict):
        """Inits Parser.

        Args:
            pql (dict): a valid PQL dict object
        """
        self.pql = self.validate_pql(pql)
        self.pipelines: typing.List[Pipeline] = []

    @staticmethod
    def validate_pql(pql: dict) -> dict:
        """

        Args:
            pql (dict): the PQL dict to be validated

        Returns:
            dict: validated pql dict that conforms to schema
        """
        try:
            validate(pql, pql_schema)
            return pql
        except ValidationError as e:
            raise PqlValidationError(
                f"PQL validation failed on {e.parent.instance if e.parent else e.instance}"
            )

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
        """Aggregates pipelines results depending on the `method`."""
        agg_method = self.pql["aggregate"]["method"]
        pipeline_results = (
            construct_aggregate_sql_payload(
                self.pipelines, self.pql["aggregate"]["params"]
            )
            if agg_method == "query.sql"
            else [Decimal(pipeline.step_results[-1]) for pipeline in self.pipelines]
        )
        if agg_method == "mean":
            return np.mean(pipeline_results)
        elif agg_method == "median":
            return np.median(pipeline_results)
        elif agg_method == "max":
            return np.amax(pipeline_results)
        elif agg_method == "min":
            return np.amin(pipeline_results)
        elif agg_method == "query.sql":
            return await execute_sql_query(
                pipeline_results,
                self.pql["aggregate"]["query"],
                self.pql["aggregate"]["result"],
            )
        else:
            raise MethodNotFound(
                f'aggregate method "{agg_method}" not found.',
            )


async def parse_and_execute(pql: dict) -> typing.Any:
    """parse_and_execute parses the initial PQL version and selects the correct Parser
    class.

    Args:
        pql (dict): a valid PQL JSON

    Returns:
        typing.Any: executed result
    """
    return await Parser(pql).execute()
