import typing
from decimal import Decimal

import pandas as pd

from src.config import config
from src.pql.exceptions import NoInputValue
from src.pql.handlers.eth_handler import EthHandler
from src.pql.handlers.rest_api_handler import RestApiHandler
from src.pql.handlers.sql_handler import SqlHandler
from src.pql.query_sql import execute_sql_query, prepare_data


class Pipeline:
    """Pipeline holds the information about the specific PQL pipeline as well as the executed results."""

    def __init__(self, pipeline: dict):
        """Initialize Pipeline object.

        Args:
            pipeline (dict): pipeline PQL json.
        """
        self.pipeline = pipeline
        self.step_results: typing.List[typing.Any] = []

    async def execute(self) -> None:
        """Execute `self.pipeline` step by step.

        Args:

        Returns:
            None: the results are available through `self.step_results`.
        """
        for i, step in enumerate(self.pipeline["pipeline"]):
            if step["step"] == "extract":
                result = await self.extract(step)
            elif step["step"] == "traverse":
                result = await self.traverse(step, i)
            elif step["step"] == "get_index":
                result = await self.get_index(step, i)
            elif step["step"] == "math":
                result = await self.math(step, i)
            elif step["step"].startswith("custom"):
                result = config.PQL_CUSTOM_METHODS[step["step"]].execute(step, i, self)
            elif step["step"] == "query.sql":
                result = await self.query_sql(step, i)

            self.step_results.append(result)

    @staticmethod
    async def extract(step: dict) -> typing.Any:
        """Parses `extract` step, finds the correct handler and executes the step.

        Args:
            step: `extract` step PQL json.

        Returns:
            typing.Any: result of the extraction.
        """
        if step["method"].startswith("http"):
            return await RestApiHandler.execute(step)
        if step["method"].startswith("sql"):
            return await SqlHandler.execute(step)
        if step["method"].startswith("eth"):
            return await EthHandler.execute(step)

    async def traverse(self, step: dict, index: int) -> typing.Any:
        """Traverse the result from the previous step given the `method`.

        Args:
            step: current step PQL json.
            index: current step index.
        """
        curr = self.get_value_for_step(index - 1)

        # Traverse through the JSON
        for level in step["params"]:
            curr = curr[level]

        return curr

    async def get_index(self, step: dict, step_index: int) -> typing.Any:
        """Get the item on step['params'] from the result from the previous step.

        Args:
            step: current step PQL json.
            index: current step index.
        """
        prev_result = self.get_value_for_step(step_index - 1)

        return prev_result[int(step["params"])]

    async def math(self, step: dict, index: int) -> Decimal:
        """Perform math operation on the previous step given the `method` and `params`.

        `div` and `sub` methods also specify `direction` param:
            - `reverse` option will perform `params` / `previous_step`,
               without `reverse` it will perform `previous_step` / `params`

        Args:
            step: step PQL json
            index: index of the step.
        """
        calculations: typing.Dict[
            tuple, typing.Callable[[Decimal, Decimal], Decimal]
        ] = {
            ("mul", "forward"): lambda curr, params: curr * params,
            ("add", "forward"): lambda curr, params: curr + params,
            ("sub", "forward"): lambda curr, params: curr - params,
            ("sub", "reverse"): lambda curr, params: params - curr,
            ("div", "forward"): lambda curr, params: curr / params,
            ("div", "reverse"): lambda curr, params: params / curr,
        }

        curr = Decimal(self.get_value_for_step(index - 1))
        params = Decimal(step["params"])

        return calculations[(step["method"], step.get("direction", "forward"))](
            curr, params
        )

    async def query_sql(self, step: dict, index: int) -> typing.Any:
        """ "Convert the data from the previous step in the pipeline to a pd.DataFrame
        and then execute the user defined sql query against it.

        Args:
            step: step PQL json
            index: index of the step

        Returns:
            typing.Any: return of the sql query processing.
        """
        data = prepare_data(self.get_value_for_step(index - 1), step["method"])
        return await execute_sql_query(data, step["query"], step.get("result"))

    def get_value_for_step(self, i: int) -> typing.Any:
        """get_value_for_step obtains the value from previous step if it exists.

        Args:
            i: step index to get the value for.

        Raises:
            NoInputValue: step value on index `i` has no value.

        Returns:
            typing.Any: step value on index `i`

        """
        if i < 0:
            raise NoInputValue(
                f"Step with index {i} has no input value.",
            )
        else:
            return self.step_results[i]
