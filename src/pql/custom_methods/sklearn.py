import typing

import sklearn_json

from src.pql.custom_methods import CustomMethod
from src.pql.query_sql import to_df


class Sklearn(CustomMethod):
    PQL_IDENTIFIER = "custom.sklearn"
    SCHEMA = {
        "type": "object",
        "properties": {
            "step": {"const": "custom.sklearn"},
            "method": {"const": "dict"},
            "model": {"type": "object"},
        },
        "required": ["step", "model", "method"],
    }

    @classmethod
    def execute(cls, step: dict, index: int, pipeline) -> typing.Any:
        model = sklearn_json.from_dict(step["model"])
        data = to_df(pipeline.get_value_for_step(index - 1), step["method"])
        prediction = list(model.predict(data))
        return prediction
