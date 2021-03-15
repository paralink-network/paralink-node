import json

import pytest

from aioresponses import aioresponses


@pytest.fixture()
def bad_step() -> dict:
    return {
        "not": "traverse",
        "correct": "json",
        "step": ["bitcoin", "usd"],
    }


@pytest.fixture()
def second_bad_step() -> dict:
    return {"second": "bad", "test": "value"}


@pytest.fixture
def pql(bad_step: dict, second_bad_step: dict):
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
                    bad_step,
                    second_bad_step,
                ],
            }
        ],
    }


async def test_pql_schema(client, pql, bad_step, second_bad_step):
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
        res = res.json()

        assert res == {
            "jsonrpc": "2.0",
            "error": {
                "code": -32006,
                "message": "\n".join(
                    [
                        f"{step} is not valid under any of the given schemas"
                        for step in [bad_step, second_bad_step]
                    ]
                ),
            },
            "id": 1,
        }
