import logging

from scalecodec.base import ScaleBytes
from substrateinterface import Keypair, SubstrateInterface
from substrateinterface.contracts import (
    ContractEvent,
    ContractInstance,
    ContractMetadata,
)

from src.network.chain import Chain
from src.network.exceptions import ChainValidationFailed

logger = logging.getLogger(__name__)


class SubstrateChain(Chain):
    """SubstrateChain is an abstraction of a parachain."""

    def __init__(
        self,
        name,
        url="ws://127.0.0.1:9944",
        credentials={},
        active=True,
        tracked_contracts=[],
        metadata_file="src/data/polkadot/oracle_metadata.json",
    ):
        """Creates SubstrateChain object.

        Args:
            url: parachain URL
            tracked_contracts: contract addresses to be listen for Request events
            metadata_file: metadata file of the oracle contract
            keypair (Keypair): Keypair with which to interact with this account
        """
        super().__init__(name, url, credentials, active, tracked_contracts)

        self.metadata_file = metadata_file

    def get_connection(self, validate_chain: bool = True) -> SubstrateInterface:
        """Connects to Substrate chain on given `url` and returns `SubstrateInterface`.

        Args:
            validate_chain: specify if the chain should be validated.

        Returns:
            SubstrateInterface: interface with which we can interact with the parachain.

        Raises:
            ConnectionRefusedError: connection could not be established.
        """
        substrate_interface = SubstrateInterface(self.url)

        if validate_chain:
            self._validate_chain(substrate_interface)

        return substrate_interface

    def check_valid_contracts(self, substrate: SubstrateInterface = None) -> None:
        """Iterates over `self.tracked_contracts` and checks whether the contract is
        deployed."""
        if not substrate:
            substrate = self.get_connection()

        for contract_address in self.tracked_contracts:
            contract_info = substrate.query(
                "Contracts", "ContractInfoOf", params=[contract_address]
            )
            if not contract_info:
                logger.warn(
                    f"[[bold]{self.name}[/]] Contract {contract_address} does not exist on chain."
                )

    def create_contract_from_address(
        self, address: str, substrate: SubstrateInterface = None
    ) -> ContractInstance:
        """Given the `address` return a ContractInstance of the contract using the
        `self.metadata_file` metadata.

        Args:
            address (str): contract address to create contract from

        Returns:
            ContractInstance: instance of the contract on the address.
        """
        if not substrate:
            substrate = self.get_connection()

        return ContractInstance.create_from_address(
            contract_address=address,
            metadata_file=self.metadata_file,
            substrate=substrate,
        )

    def get_block_events(self, block_hash: str) -> list:
        """Find `Request` events for the given `block_hash`.

        Args:
            block_hash (str): block hash for which to find event.

        Returns:
            list: list of tuples (event, decoded_event), where `event` represents a raw
            `Request` events and `decoded_event` is a dict of the decoded event.
        """
        substrate = self.get_connection()
        spec_version = substrate.get_block_runtime_version(block_hash).get(
            "specVersion", 0
        )

        # Obtain metadata
        metadata = substrate.get_block_metadata(block_hash, spec_version)
        contract_metadata = ContractMetadata.create_from_file(
            self.metadata_file, substrate
        )

        # Iterate through raw events in the block
        new_events = []
        for event in substrate.get_block_events(block_hash, metadata).elements:
            if (
                event.event_module.name == "Contracts"
                and event.event.name == "ContractExecution"
            ):
                contract_event_obj = ContractEvent(
                    data=ScaleBytes(event.params[1]["value"]),
                    runtime_config=substrate.runtime_config,
                    contract_metadata=contract_metadata,
                )
                decoded_event = contract_event_obj.decode()

                # Request event was found, add it to the list
                if decoded_event["name"] == "Request":
                    if (
                        substrate.ss58_encode(event.params[0]["value"])
                        in self.tracked_contracts
                    ):
                        new_events.append((event, decoded_event))

        return new_events

    def fulfill(self, contract: ContractInstance, args: dict, res: int) -> None:
        keypair = Keypair.create_from_private_key(
            private_key=self.credentials["private_key"],
            public_key=self.credentials["public_key"],
        )

        # Estimate gas fee
        predicted_gas = contract.read(
            keypair,
            "simple_callback",
            args={
                "request_id": args["request_id"],
                "callback_addr": args["from"],
                "result": {"Numeric": res},
            },
        )

        logger.debug(
            f"[[bold]{self.name}[/]] Estimating gas fee: {predicted_gas.gas_consumed}"
        )

        # Execute call
        receipt = contract.exec(
            keypair,
            "simple_callback",
            args={
                "request_id": args["request_id"],
                "callback_addr": args["from"],
                "result": {"Numeric": res},
            },
            gas_limit=predicted_gas.gas_consumed * 2,
        )

        logger.info(f"[[bold]{self.name}[/]] Callback substrate receipt: {receipt}")

        if receipt.is_succes:
            # Log the callback completed events
            for contract_event in receipt.contract_events:
                logger.info(
                    f"[[bold]{self.name}[/]] Contract callback events {contract_event.name} {contract_event.docs}:  {contract_event.value}"
                )
        else:
            raise Exception(
                f"[[bold]{self.name}[/]] Contract fulfill request {args} unsuccessful {receipt.error_message}"
            )

        # Read back the result
        result = contract.read(
            keypair, "oracle_results", args={"request_id": args["request_id"]}
        )
        logger.info(
            f"[[bold]{self.name}[/]] Reading the value from contract after the callback {result}",
        )

    def _validate_chain(self, substrate_interface: SubstrateInterface) -> None:
        """Validates the SubstrateInterface is connected to the expected chain.

        Raises:
            ChainValidationFailed: if the chain fails validation.
        """
        if self.name != substrate_interface.chain.lower():
            raise ChainValidationFailed(
                f"Chain validation failed for {self.name} "
                f"- Expected chain name: {self.name} "
                f"- Actual: {substrate_interface.chain}"
            )
