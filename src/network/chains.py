import json

from src.network.evm_chain import EvmChain
from src.network.substrate_chain import SubstrateChain


class Chains:
    """Chains holds the information about the different blockchains served by the node."""

    def __init__(self, evm={}, substrate={}):
        """Inits empty Chains object.

        Args:
            evm: a dict of {name: EvmChain} objects
            substrate: a dict of {name: SubstrateChain} objects
        """
        self.evm = evm
        self.substrate = substrate

    @classmethod
    def read_from_sql(cls) -> "Chains":
        # TODO
        return cls()

    @classmethod
    def read_from_json(cls, json_path: str) -> "Chains":
        """read_from_json parses the JSON chain_config file and returns it as a `Chains`
        object.

        Args:
            json_path (str): path to the JSON

        Returns:
            "Chains": Chains object with parsed data.
        """
        with open(json_path, "r") as chain_config_file:
            chain_config = json.load(chain_config_file)

            evm = {}
            substrate = {}
            for chain in chain_config:
                if "enabled" in chain and chain["enabled"]:
                    if chain["type"] == "evm":
                        evm[chain["name"]] = EvmChain(
                            name=chain["name"],
                            url=chain["url"],
                            credentials=chain.get("credentials", {}),
                            tracked_contracts=chain.get("tracked_contracts", []),
                        )
                    elif chain["type"] == "substrate":
                        substrate[chain["name"]] = SubstrateChain(
                            name=chain["name"],
                            url=chain["url"],
                            credentials=chain.get("credentials", {}),
                            tracked_contracts=chain.get("tracked_contracts", []),
                            metadata_file=chain.get(
                                "metadata_file",
                                "src/data/polkadot/oracle_metadata.json",
                            ),
                        )

            return cls(evm, substrate)
