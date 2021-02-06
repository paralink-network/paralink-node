import asyncio
import json

from src.config import config
from src.models import Chain, ContractOracle, db
from src.network.evm_chain import EvmChain
from src.network.substrate_chain import SubstrateChain

if config.ENABLE_DATABASE:
    asyncio.get_event_loop().run_until_complete(db.set_bind(config.DATABASE_URL))


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
        """extract chain and contract data from database, instantiate appropriate chains
        and return `Chains` object.

        Returns:
            "Chains": chains object with parsed data.
        """
        chain_data, contract_data = asyncio.get_event_loop().run_until_complete(
            Chains._get_chains_and_contracts_from_database()
        )
        for chain in chain_data:
            chain["tracked_contracts"] = [
                contract["id"]
                for contract in contract_data
                if contract["active"] and contract["chain"] == chain["name"]
            ]
        return cls.chain_factory(chain_data)

    @staticmethod
    async def _get_chains_and_contracts_from_database():
        chain_data = await Chain.query.gino.all()
        contract_data = await ContractOracle.query.gino.all()
        return [x.serialize for x in chain_data], [x.serialize for x in contract_data]

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

            return cls.chain_factory(chain_config)

    @classmethod
    def chain_factory(cls, chain_config):
        evm = {}
        substrate = {}
        for chain in chain_config:
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
                        "metadata_file", "src/data/polkadot/oracle_metadata.json"
                    ),
                )
        return cls(evm, substrate)
