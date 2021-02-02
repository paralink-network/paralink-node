import json
import logging
import typing

from web3 import Web3

from src.config import config
from src.network.chain import Chain
from src.network.exceptions import ChainValidationFailed

logger = logging.getLogger(__name__)
chain_reference_data = json.load(open("src/data/chains.json"))


def fetch_chain_data(name: str) -> dict:
    """A function to fetch chain reference data.

    Args:
        name (str): chain name.

    Returns:
        reference data associated with chain_id and network_id.

    Raises:
        ChainReferenceDataNotFound: if reference data is not found.
    """
    short_name, network = name.split(".")
    for chain in chain_reference_data:
        if chain["shortName"] == short_name and chain["network"] == network:
            return chain
    return {}


class EvmChain(Chain):
    def __init__(
        self,
        name,
        url="ws://localhost:8545",
        credentials={},
        active=True,
        tracked_contracts=[],
        oracle_metadata=config.ORACLE_CONTRACT_ABI,
    ):
        self.chain_data = fetch_chain_data(name)
        self.oracle_metadata = oracle_metadata
        super().__init__(name, url, credentials, active, tracked_contracts)

    def get_connection(self) -> Web3:
        """Return Web3 connection to the chain specified by `url`."""
        if self.url.startswith("ws"):
            web3 = Web3(Web3.WebsocketProvider(self.url))
        elif self.url.startswith("http"):
            web3 = Web3(Web3.HTTPProvider(self.url))
        else:
            raise ValueError("URL type not supported")

        if self.chain_data and (
            int(web3.net.version) != self.chain_data["networkId"]
            or web3.eth.chainId != self.chain_data["chainId"]
        ):
            raise ChainValidationFailed(
                f"Chain validation failed for {self.name} "
                f"- Expected (chainId, networkId): ({self.chain_data['chainId'], self.chain_data['networkId']}) "
                f"- Actual: ({web3.eth.chainId}, {web3.net.version})"
            )

        return web3

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
