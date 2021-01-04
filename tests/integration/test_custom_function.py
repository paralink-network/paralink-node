import json
from unittest.mock import MagicMock

import pytest
from aioresponses import aioresponses


@pytest.fixture
def pql():
    return {
        "name": "Custom function",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Bitcoin price CoinGecko",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                    },
                    {
                        "step": "traverse",
                        "method": "json",
                        "params": ["bitcoin", "usd"],
                    },
                    {"step": "custom.my_add", "params": 10000,},
                ],
            }
        ],
    }


async def test_custom_function_not_found(client, pql):
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        m.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            payload={"bitcoin": {"usd": 25000}},
        )

        request = {
            "jsonrpc": "2.0",
            "method": "execute_pql",
            "params": json.dumps(pql),
            "id": 1,
        }
        res = await client.post("/rpc", json=request)
        res = await res.json()

        assert res == {
            "jsonrpc": "2.0",
            "error": {
                "code": -32010,
                "message": 'custom step "custom.my_add" not found',
            },
            "id": 1,
        }


async def test_custom_function(client, mocker, pql):
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        m.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            payload={"bitcoin": {"usd": 25000}},
        )

        PQL_CUSTOM_METHODS = {
            "my_add": lambda step, index, pipeline: pipeline.get_value_for_step(
                index - 1
            )
            + step["params"]
        }

        mocker.patch.dict(
            "src.pql.pipeline.config.PQL_CUSTOM_METHODS", PQL_CUSTOM_METHODS
        )

        request = {
            "jsonrpc": "2.0",
            "method": "execute_pql",
            "params": json.dumps(pql),
            "id": 1,
        }
        res = await client.post("/rpc", json=request)
        res = await res.json()

        assert res == {"jsonrpc": "2.0", "result": "35000", "id": 1}
