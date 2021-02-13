import logging
import typing

from web3 import Web3

from src.config import config
from src.network.chain import Chain

logger = logging.getLogger(__name__)


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
        super().__init__(name, url, credentials, active, tracked_contracts)

        self.oracle_metadata = oracle_metadata

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
            f"[[bold]{self.name}[/]] Fulfill request{args['requestId']} with value {res}."
        )

        eth_key = w3.eth.account.from_key(self.credentials["private_key"])

        tx = contract.functions.fulfillRequest(
            args["requestId"],
            args["fee"],
            args["callbackAddress"],
            args["callbackFunctionId"],
            args["expiration"],
            w3.toBytes(int(res)).rjust(32, b"\0"),
        ).buildTransaction({"from": eth_key.address})

        tx["gas"] *= 2
        tx.update({"nonce": w3.eth.getTransactionCount(eth_key.address)})

        signed_tx = w3.eth.account.signTransaction(tx, eth_key.privateKey)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

        logger.info(f"[[bold]{self.name}[/]] Received TX receipt: {tx_receipt}")
