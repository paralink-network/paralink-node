from asyncio import get_event_loop
import json

from aiohttp import ClientSession


async def main():
    """Performs a balance request as well as custom function call to the ETH node.
    Calls in the past require an archive node.
    """
    url = "http://127.0.0.1:7424"

    pql = {
        "name": "Ethereum request",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Custom function call on ETH contract",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "eth.function",
                        "address": "0xBb2b8038a1640196FbE3e38816F3e67Cba72D940",
                        "params": {
                            "function": "balanceOf(address)",
                            "args": ["0x9b89202Fc32c294Df4B2b52830fF40B3EC0F0369"],
                            "block": 11514560,  # optional (defaults to 'latest')
                            # Should return 2912396840
                        },
                    },
                ],
            },
            {
                "name": "Address ETH balance",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "eth.balance",
                        "address": "0x9b89202Fc32c294Df4B2b52830fF40B3EC0F0369",
                        "params": {
                            "block": 11514560,  # optional (defaults to 'latest')
                        },
                    },
                ],
            },
        ],
    }

    # Construct JSON RPC request
    request = {
        "jsonrpc": "2.0",
        "method": "execute_pql",
        "params": json.dumps(pql),
        "id": 1,
    }

    async with ClientSession() as session:
        async with session.post(url + "/rpc", json=request) as resp:
            response = await resp.json()
            print(response)


if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
