from asyncio import get_event_loop
import json

from aiohttp import ClientSession


async def main():
    """Obtains Bitcoin price from a single API endpoint.
    """
    url = "http://127.0.0.1:7424"

    pql_bitcoin_price = {
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
                    }
                ],
            },
            {
                "name": "Bitcoin price Bitfinex",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api-pub.bitfinex.com/v2/ticker/tBTCUSD",
                    }
                ],
            },
            {
                "name": "Bitcoin price CoinDesk",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api.coindesk.com/v1/bpi/currentprice.json",
                    }
                ],
            },
        ],
        "aggregate": {
            "method": "query.sql",
            "parsers": ["json", "list", "json"],
            "query": "SELECT AVG(price) FROM (SELECT `bitcoin.usd` AS price FROM result_0 UNION SELECT `6` AS price FROM result_1 UNION SELECT `bpi.USD.rate_float` AS price FROM result_2)",
            "result": True,
        },
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
