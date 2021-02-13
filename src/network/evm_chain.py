import logging
import typing

from web3 import Web3

from src.config import config
from src.network.chain import Chain
from src.network.exceptions import ChainValidationFailed

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
        evm_chain_reference_data=config.EVM_CHAIN_REFERENCE_DATA,
    ):
        super().__init__(name, url, credentials, active, tracked_contracts)

        self.oracle_metadata = oracle_metadata
        self.evm_chain_reference_data = evm_chain_reference_data

    def get_connection(self, validate_chain: bool = True) -> Web3:
        """Return Web3 connection to the chain specified by `url`.

        Args:
            validate_chain: specify if the chain should be validated.

        Returns:
            Web3: web3 client used to interact with the evm chain.
        """
        if self.url.startswith("ws"):
            w3 = Web3(Web3.WebsocketProvider(self.url))
        elif self.url.startswith("http"):
            w3 = Web3(Web3.HTTPProvider(self.url))
        else:
            raise ValueError("URL type not supported")

        if validate_chain:
            self._validate_chain(w3)

        return w3

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

    def _validate_chain(self, w3: Web3) -> None:
        """Validates the web3 instance has the expected chainId and networkId.

        Raises:
            ChainValidationFailed: if the chain fails validation
        """
        chain_data = self._get_evm_chain_reference_data()

        if chain_data and (
            int(w3.net.version) != chain_data["networkId"]
            or w3.eth.chainId != chain_data["chainId"]
        ):
            raise ChainValidationFailed(
                f"Chain validation failed for {self.name} "
                f"- Expected (chainId, networkId): {chain_data['chainId'], chain_data['networkId']} "
                f"- Actual: {w3.eth.chainId, int(w3.net.version)}"
            )

    def _get_evm_chain_reference_data(self) -> dict:
        """A function to fetch evm chain reference data.

        Returns:
            reference data associated with chain_id and network_id.
        """
        short_name, network = self.name.split(".")
        for chain in self.evm_chain_reference_data:
            if chain["shortName"] == short_name and chain["network"] == network:
                return chain
        return {}
