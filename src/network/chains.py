import json
from typing import Optional

from sqlalchemy.orm.session import Session

from src.models.chain import Chain as ChainDb
from src.network.chain import Chain
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

    async def from_sql(self, session: Session) -> "Chains":
        """Fetch chain and contract data from database and update Chains to reflect.

        Args:
            session (Session): sqlalchemy session

        Returns:
            Chains: a self reference
        """
        chain_data = await ChainDb.get_chains(session)
        for chain in chain_data:
            target_chain = self.get_chain(chain.name)
            if target_chain is not None:
                target_chain.active = chain.active
                target_chain.tracked_contracts = [
                    contract.address for contract in chain.contracts if contract.active
                ]

        return self

    @classmethod
    def from_list(cls, chain_config: list) -> "Chains":
        """from_list parses the chain_config list and returns it as a `Chains`
        object.

        Args:
            chain_config (list): list of Chain configurations.

        Returns:
            "Chains": Chains object with parsed data.
        """
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

    def get_chain(self, chain: str) -> Optional[Chain]:
        if chain in self.evm:
            return self.evm[chain]
        elif chain in self.substrate:
            return self.substrate[chain]
        else:
            return None

    def get_chains(self) -> dict:
        return {**self.evm, **self.substrate}
