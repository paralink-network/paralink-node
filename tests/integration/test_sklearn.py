import json

import pytest

import pandas as pd
from aioresponses import aioresponses
from sklearn import datasets


@pytest.fixture()
def linear_regression_model() -> dict:
    return {
        "meta": "linear-regression",
        "coef_": [
            -10.012197817470847,
            -239.81908936565472,
            519.8397867901343,
            324.3904276893763,
            -792.1841616283061,
            476.74583782366255,
            101.04457032134488,
            177.0641762322512,
            751.2793210873945,
            67.62538639104386,
        ],
        "intercept_": 152.1334841628965,
        "params": {
            "copy_X": True,
            "fit_intercept": True,
            "n_jobs": None,
            "normalize": False,
            "positive": False,
        },
    }


@pytest.fixture()
def sample_data() -> tuple:
    diabetes_x, _ = datasets.load_diabetes(return_X_y=True)
    return pd.DataFrame(diabetes_x).iloc[:10, :].to_dict()


async def test_sklearn(client, linear_regression_model, sample_data):
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        m.get(
            "https://sample-data.com/",
            payload=sample_data,
        )

        get_pql = {
            "name": "sklearn prediction",
            "psql_version": "0.1",
            "sources": [
                {
                    "name": "Bitfinex BTC price GET request",
                    "pipeline": [
                        {
                            "step": "extract",
                            "method": "http.get",
                            "uri": "https://sample-data.com/",
                        },
                        {
                            "step": "custom.sklearn",
                            "method": "dict",
                            "model": linear_regression_model,
                        },
                    ],
                }
            ],
        }

        request = {
            "jsonrpc": "2.0",
            "method": "execute_pql",
            "params": json.dumps(get_pql),
            "id": 1,
        }
        res = await client.post("/rpc", json=request)
        res = await res.json()

        assert (
            res["result"]
            == "[206.1170697870923, 68.07234760996164, 176.88406035049724, 166.91796558989097, 128.4598424093249, 106.34908971549203, 73.8941794736001, 118.85378668710919, 158.81033075835248, 213.58408892913423]"
        )
