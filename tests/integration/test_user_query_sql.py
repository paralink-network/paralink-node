import json

from aioresponses import aioresponses


async def test_user_query(client):
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
                            "step": "query.sql",
                            "method": "json",
                            "query": "SELECT `bitcoin.usd` FROM response",
                            "result": True,
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

        assert res == {"jsonrpc": "2.0", "result": "25000", "id": 1}
