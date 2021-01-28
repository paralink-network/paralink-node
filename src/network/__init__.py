import json
from pathlib import Path

from src.config import config
from src.network.chains import Chains

chain_config = Path(config.DATA_FOLDER).joinpath("chain_config.json")
chains = Chains.read_from_json(str(chain_config.absolute()))
