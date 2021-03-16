import json

from aioresponses import aioresponses


async def test_http_get(client):
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        m.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            payload={"bitcoin": {"usd": 25000}},
        )

        get_pql = {
            "name": "GET HTTP",
            "psql_version": "0.1",
            "sources": [
                {
                    "name": "Bitfinex BTC price GET request",
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
        res = res.json()

        assert res == {"jsonrpc": "2.0", "result": "25000", "id": 1}


async def test_http_post(client):
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        m.post(
            "https://api-pub.bitfinex.com/v2/calc/fx",
            payload=[22695],
        )
        post_pql = {
            "name": "POST HTTP",
            "psql_version": "0.1",
            "sources": [
                {
                    "name": "Bitfinex BTC price POST request",
                    "pipeline": [
                        {
                            "step": "extract",
                            "method": "http.post",
                            "uri": "https://api-pub.bitfinex.com/v2/calc/fx",
                            "params": {"ccy1": "BTC", "ccy2": "USD"},
                        },
                        {
                            "step": "get_index",
                            "params": 0,
                        },
                    ],
                },
            ],
        }

        request = {
            "jsonrpc": "2.0",
            "method": "execute_pql",
            "params": json.dumps(post_pql),
            "id": 1,
        }
        res = await client.post("/rpc", json=request)
        res = res.json()

        assert res == {"jsonrpc": "2.0", "result": "22695", "id": 1}
