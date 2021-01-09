from decimal import Decimal
import typing

from src.pql.exceptions import StepNotFound, MethodNotFound, NoInputValue
from src.pql.handlers.rest_api_handler import RestApiHandler
from src.pql.handlers.sql_handler import SqlHandler
from src.pql.handlers.eth_handler import EthHandler
from src.pql.common import execute_user_query, to_df
from src.config import config


class Pipeline:
    """Pipeline holds the information about the specific PQL pipeline as well as the executed results.
    """

    def __init__(self, pipeline: dict):
        """Initialize Pipeline object.

        Args:
            pipeline (dict): pipeline PQL json.
        """
        self.pipeline = pipeline
        self.step_results = []

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
                custom_step = step["step"].split(".")[-1]

                if custom_step in config.PQL_CUSTOM_METHODS:
                    result = config.PQL_CUSTOM_METHODS[custom_step](step, i, self)

                else:
                    raise StepNotFound(f"custom step \"{step['step']}\" not found")
            elif step["step"] == "user_query":
                result = await self.user_query(step, i)
            else:
                raise StepNotFound(f"step \"{step['step']}\" not found")

            self.step_results.append(result)

    async def extract(self, step: dict) -> typing.Any:
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
        else:
            raise MethodNotFound(
                f"handler for extract step method \"{step['method']}\" not found.",
            )

    async def traverse(self, step: dict, index: int) -> typing.Any:
        """Traverse the result from the previous step given the `method`.

        Args:
            step: current step PQL json.
            index: current step index.
        """
        if step["method"] == "json":
            curr = self.get_value_for_step(index - 1)

            # Traverse through the JSON
            for level in step["params"]:
                curr = curr[level]

            return curr
        else:
            raise MethodNotFound(
                f"handler for traverse step method \"{step['method']}\" not found."
            )

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
        curr = Decimal(self.get_value_for_step(index - 1))
        params = Decimal(step["params"])

        if step["method"] == "mul":
            return curr * params
        elif step["method"] == "add":
            return curr + params
        elif step["method"] == "sub":
            if "direction" in step and step["direction"] == "reverse":
                return params - curr
            else:
                return curr - params
        elif step["method"] == "div":
            if "direction" in step and step["direction"] == "reverse":
                return params / curr
            else:
                return curr / params
        else:
            raise MethodNotFound(
                f"handler for math step method \"{step['method']}\" not found."
            )

    async def user_query(self, step: dict, index: int):
        df = to_df(self.get_value_for_step(index - 1), step["parser"])
        return await execute_user_query(
            {"response": df}, step["query"], step.get("result")
        )

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
            raise NoInputValue(f"Step with index {i} has no input value.",)
        else:
            return self.step_results[i]
