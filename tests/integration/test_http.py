async def test_http_get(client):
    js = ({"jsonrpc": "2.0", "method": "execute_pql", "id": 1},)
    res = await client.post("/rpc", json=js)
    print(await res.json())
