from asyncio import get_event_loop
import json

from aiohttp import ClientSession


async def main():
    """Obtains Bitcoin price from a single API endpoint.
    """
    url = "http://127.0.0.1:7424"

    pql_bitcoin_price = {
        "name": "simple http get request",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "bitcoin price etl",
                "pipeline": [
                    # first perform http get request to coingecko api
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                    },
                    # the resulting json will look like
                    # {
                    # "bitcoin": {
                    # "usd": 20551
                    # }
                    # }
                    # therefore we have to traverse the json
                    {
                        "step": "traverse",
                        "method": "json",
                        "params": ["bitcoin", "usd"],
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
