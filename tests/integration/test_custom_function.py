import json

import pytest

from aioresponses import aioresponses


@pytest.fixture()
def custom_step() -> dict:
    return {"step": "custom.my_add", "params": 10000}


@pytest.fixture
def bad_custom_step() -> dict:
    return {"step": "i_dont_exist", "params": 1000}


@pytest.fixture
def pql(custom_step: dict):
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
                    custom_step,
                ],
            }
        ],
    }


@pytest.fixture
def bad_custom_step_pql(bad_custom_step: dict):
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
                    bad_custom_step,
                ],
            }
        ],
    }


async def test_custom_function_not_found(client, bad_custom_step_pql, bad_custom_step):
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        m.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            payload={"bitcoin": {"usd": 25000}},
        )

        request = {
            "jsonrpc": "2.0",
            "method": "execute_pql",
            "params": json.dumps(bad_custom_step_pql),
            "id": 1,
        }
        res = await client.post("/rpc", json=request)
        res = await res.json()

        assert res == {
            "jsonrpc": "2.0",
            "error": {
                "code": -32006,
                "message": f"{bad_custom_step} is not valid under any of the given schemas",
            },
            "id": 1,
        }


async def test_custom_function(client, mocker, pql):
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

        assert res == {"jsonrpc": "2.0", "result": "35000", "id": 1}
