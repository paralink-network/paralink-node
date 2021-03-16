import json
from unittest.mock import AsyncMock


async def test_psql_connection(client, mocker):
    # Mock PSQL connection
    obj = AsyncMock()
    obj.fetch.return_value = [{"symbol": "BTC", "price": 20000}]
    mocker.patch("src.pql.handlers.sql_handler.asyncpg.connect", return_value=obj)

    # Define PQL
    sql_pql = {
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
                    {
                        "step": "get_index",
                        "params": 0,
                    },
                    {
                        "step": "traverse",
                        "method": "json",
                        "params": ["price"],
                    },
                ],
            }
        ],
    }

    request = {
        "jsonrpc": "2.0",
        "method": "execute_pql",
        "params": json.dumps(sql_pql),
        "id": 1,
    }
    res = await client.post("/rpc", json=request)
    res = res.json()

    assert res == {"jsonrpc": "2.0", "result": "20000", "id": 1}
