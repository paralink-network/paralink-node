from asyncio import get_event_loop
import json

from aiohttp import ClientSession


async def main():
    url = "http://127.0.0.1:7424"

    pql_bitcoin_price = {
        "name": "Simple HTTP GET request",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Bitcoin price ETL",
                "pipeline": [
                    # First perform HTTP GET request to CoinGecko API
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                    },
                    # The resulting JSON will look like
                    # {
                    # "bitcoin": {
                    # "usd": 20551
                    # }
                    # }
                    # Therefore we have to traverse the JSON
                    {
                        "step": "traverse",
                        "method": "json",
                        "levels": ["bitcoin", "usd"],
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
            # print(response["result"])  # 19
            print(response)


if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
