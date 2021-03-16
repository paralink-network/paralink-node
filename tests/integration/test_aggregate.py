import json

import pytest

from aioresponses import aioresponses


@pytest.fixture
def pql_json():
    return {
        "name": "Aggregate HTTP requests",
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
                ],
            },
            {
                "name": "Bitcoin price Bitfinex",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api-pub.bitfinex.com/v2/ticker/tBTCUSD",
                    },
                    {
                        "step": "get_index",
                        "params": 6,
                    },
                ],
            },
            {
                "name": "Bitcoin price CoinDesk",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api.coindesk.com/v1/bpi/currentprice.json",
                    },
                    {
                        "step": "traverse",
                        "method": "json",
                        "params": ["bpi", "USD", "rate_float"],
                    },
                ],
            },
        ],
        "aggregate": {"method": "mean"},
    }


@pytest.fixture
def mock_responses():
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        # Mock the responses
        m.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            payload={"bitcoin": {"usd": 27000}},
        )

        m.get(
            "https://api-pub.bitfinex.com/v2/ticker/tBTCUSD",
            payload=[
                23153,
                6.66561211,
                23160,
                15.075915900000005,
                -562.878036,
                -0.0237,
                25000,
                16378.92456368,
                24244,
                21884,
            ],
        )

        m.get(
            "https://api.coindesk.com/v1/bpi/currentprice.json",
            payload={
                "time": {
                    "updated": "Dec 21, 2020 16:59:00 UTC",
                    "updatedISO": "2020-12-21T16:59:00+00:00",
                    "updateduk": "Dec 21, 2020 at 16:59 GMT",
                },
                "disclaimer": "This data was produced from the CoinDesk Bitcoin Price Index (USD). Non-USD currency data converted using hourly conversion rate from openexchangerates.org",
                "chartName": "Bitcoin",
                "bpi": {
                    "USD": {
                        "code": "USD",
                        "symbol": "&#36;",
                        "rate": "23,244.5322",
                        "description": "United States Dollar",
                        "rate_float": 20000,
                    },
                    "GBP": {
                        "code": "GBP",
                        "symbol": "&pound;",
                        "rate": "17,460.0374",
                        "description": "British Pound Sterling",
                        "rate_float": 17460.0374,
                    },
                    "EUR": {
                        "code": "EUR",
                        "symbol": "&euro;",
                        "rate": "19,035.8772",
                        "description": "Euro",
                        "rate_float": 19035.8772,
                    },
                },
            },
        )

        yield m


@pytest.mark.parametrize(
    "method,expected_value",
    [("mean", "24000"), ("median", "25000"), ("max", "27000"), ("min", "20000")],
)
async def test_mean(client, pql_json, mock_responses, method, expected_value):
    pql_json["aggregate"]["method"] = method

    request = {
        "jsonrpc": "2.0",
        "method": "execute_pql",
        "params": json.dumps(pql_json),
        "id": 1,
    }
    res = await client.post("/rpc", json=request)
    res = res.json()

    assert res["result"] == expected_value
