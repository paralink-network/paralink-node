import json
from asyncio import get_event_loop

from aiohttp import ClientSession


async def main():
    """Custom function example (custom.my_add).

    The function should be specified in src.config.Config PQL_CUSTOM_METHODS dictionary, such as:

        PQL_CUSTOM_METHODS = {
            "my_add": lambda step, index, pipeline: pipeline.get_value_for_step(index - 1) + step["params"]
        }
    """
    url = "http://127.0.0.1:7424"

    pql_bitcoin_price = {
        "name": "my_add custom function",
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
                    # Here we call our custom function
                    {
                        "step": "custom.my_add",
                        "params": 10000,
                    },
                ],
            }
        ],
    }

    # Construct JSON RPC request
    request = {
        "jsonrpc": "2.0",
        "method": "execute_pql",
        "params": json.dumps(pql_bitcoin_price),
        "id": 1,
    }

    async with ClientSession() as session:
        async with session.post(url + "/rpc", json=request) as resp:
            response = await resp.json()
            print(response)


if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
