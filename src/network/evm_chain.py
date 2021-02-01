import json
import logging
import typing

from web3 import Web3

from src.config import config
from src.network.chain import Chain
from src.network.exceptions import ChainReferenceDataNotFound

logger = logging.getLogger(__name__)
chain_reference_data = json.load(open("src/data/chains.json"))


def fetch_chain_data(chain_id: int) -> dict:
    """A function to fetch chain reference data.

    Args:
        chain_id (int): chain ID.

    Returns:
        reference data associated with chain_id and network_id.

    Raises:
        ChainReferenceDataNotFound: if reference data is not found.
    """
    chain = [x for x in chain_reference_data if x["chainId"] == chain_id]
    if len(chain) < 1:
        raise ChainReferenceDataNotFound(
            f"Reference data not found for chain_id: {chain}"
        )
    return chain[0]


class EvmChain(Chain):
    def __init__(
        self,
        chain_id,
        url="ws://localhost:8545",
        credentials={},
        active=True,
        tracked_contracts=[],
        oracle_metadata=config.ORACLE_CONTRACT_ABI,
    ):
        self.chain_id = chain_id
        self.chain_data = fetch_chain_data(chain_id)
        self.oracle_metadata = oracle_metadata
        super().__init__(
            self.chain_data["name"], url, credentials, active, tracked_contracts
        )

    def get_connection(self) -> Web3:
        """ Return Web3 connection to the chain specified by `url`"""
        if self.url.startswith("ws"):
            return Web3(Web3.WebsocketProvider(self.url))
        elif self.url.startswith("http"):
            return Web3(Web3.HTTPProvider(self.url))
        else:
            raise ValueError("URL type not supported")

    def fulfill(self, event: dict, res: typing.Any) -> None:
        """It writes `res` (result of the PQL definition) to the location specified in the `Request` event.

        Args:
            event: a Request event from ETH chain.
            res: already executed PQL definition
        """
        w3 = self.get_connection()

        args = event["args"]
        contract = w3.eth.contract(abi=self.oracle_metadata, address=event["address"])

        logger.info(
            f"[{self.name}] Fullfil request{args['requestId']} with value {res}."
        )

        tx = contract.functions.fulfillRequest(
            args["requestId"],
            args["callbackAddress"],
            args["callbackFunctionId"],
            args["expiration"],
            w3.toBytes(int(res)).rjust(32, b"\0"),
        ).buildTransaction()

        eth_key = w3.eth.account.from_key(self.credentials["private_key"])

        tx.update({"nonce": w3.eth.getTransactionCount(eth_key.address)})

        signed_tx = w3.eth.account.signTransaction(tx, eth_key.privateKey)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

        logger.info(f"[{self.name}] Received TX receipt: {tx_receipt}")
