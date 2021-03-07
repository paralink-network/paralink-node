import json
from pathlib import Path

from src.config import config
from src.network.chains import Chains

chain_config = Path(config.DATA_FOLDER).joinpath("chain_config.json")
chains = Chains.from_list(
    json.load(open(Path(config.DATA_FOLDER).joinpath("chain_config.json")))
)  # str(chain_config.absolute()))
