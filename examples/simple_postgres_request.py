from asyncio import get_event_loop
import json

from aiohttp import ClientSession


async def main():
    """Obtains Bitcoin price from a PostgreSQL DB.

    You should first change the URI of SQL to your local instance.
    """
    url = "http://127.0.0.1:7424"

    pql_bitcoin_price = {
        "name": "Simple SQL request",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Bitcoin price PostgreSQL",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "sql.postgres",
                        "uri": "postgres://user:password@localhost/my_database_name",
                        "query": "select * FROM (VALUES ('BTC', 20000)) AS t (symbol, price);",
                    },
                    {"step": "get_index", "params": 0,},
                    {"step": "traverse", "method": "json", "params": ["price"],},
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
