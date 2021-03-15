import json

from aioresponses import aioresponses

the_graph_uniswap_query = """{
  uniswapFactories(first: 5) {
    id
    pairCount
    totalVolumeUSD
  }
  tokens(first: 5) {
    id
    symbol
    name
    decimals
  }
}
"""

the_graph_response = {
    "data": {
        "tokens": [
            {
                "decimals": "0",
                "id": "0x0000000000004946c0e9f43f4dee607b0ef1fa1c",
                "name": "Chi Gastoken by 1inch",
                "symbol": "CHI",
            },
            {
                "decimals": "18",
                "id": "0x0000000000085d4780b73119b644ae5ecd22b376",
                "name": "TrueUSD",
                "symbol": "TUSD",
            },
            {
                "decimals": "18",
                "id": "0x0000000000095413afc295d19edeb1ad7b71c952",
                "name": "Tokenlon",
                "symbol": "LON",
            },
            {
                "decimals": "8",
                "id": "0x00000000001876eb1444c986fd502e618c587430",
                "name": "Dharma Dai",
                "symbol": "dDai",
            },
            {
                "decimals": "2",
                "id": "0x0000000000b3f879cb30fe243b4dfee438691c04",
                "name": "Gastoken.io",
                "symbol": "GST2",
            },
        ],
        "uniswapFactories": [
            {
                "id": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
                "pairCount": 29087,
                "totalVolumeUSD": "71277206891.6697525914387439057691",
            }
        ],
    }
}


async def test_graphql(client):
    with aioresponses(passthrough=["http://127.0.0.1:"]) as m:
        m.post(
            "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
            payload=the_graph_response,
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
                            "uri": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
                            "params": {"query": the_graph_uniswap_query},
                        },
                        {
                            "step": "traverse",
                            "method": "json",
                            "params": ["data"],
                        },
                        {
                            "step": "query.sql",
                            "method": ["json", "json"],
                            "query": "SELECT sum(decimals) FROM tokens",
                            "result": True,
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

        assert res == {"jsonrpc": "2.0", "result": "46", "id": 1}
