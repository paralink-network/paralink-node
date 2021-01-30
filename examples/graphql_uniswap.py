import json
from asyncio import get_event_loop

from aiohttp import ClientSession

the_graph_uniswap_query = """{
  uniswapFactories(first: 5) {
    id
    pairCount
    totalVolumeUSD
  }
  tokens(first: 5) {
    tradeVolumeUSD
  }
}
"""


async def main():
    """Obtains a sum of the tradeVolumeUSD for the first 5 tokens on uniswap"""
    url = "http://127.0.0.1:7424"

    the_graph_uniswap_trade_volume = {
        "name": "GraphQL POST HTTP",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Uniswap data from The Graph",
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
                        "query": "SELECT sum(tradeVolumeUSD) FROM tokens",
                        "result": True,
                    },
                ],
            },
        ],
    }

    # Construct JSON RPC request
    request = {
        "jsonrpc": "2.0",
        "method": "execute_pql",
        "params": json.dumps(the_graph_uniswap_trade_volume),
        "id": 1,
    }

    async with ClientSession() as session:
        async with session.post(url + "/rpc", json=request) as resp:
            response = await resp.json()
            print(response)


if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
