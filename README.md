![](https://paralink.network/images/logo-sm-home.png)

# Overview ![paralink-node CI](https://github.com/paralink-network/paralink-node/workflows/paralink-node%20CI/badge.svg)

Paralink Node is responsible for executing ETL pipelines and PQL queries. The results are relayed to
all supported chains via callbacks. Paralink Node is also a dependency to the on-chain [runtime](https://github.com/paralink-network/paralink-substrate).

## Configure
Before running the node, please setup your `.env`. Copy the `.env.template` file to `.env` and modify the variables. 

Paralink node uses local configuration stored in `~/.paralink`. On the first run a default chain config will be created (`~/.paralink/chain_config.json`). Modify it to 

### Database

A PostgreSQL DB is required for node to function. Migrate the DB with:

```
pipenv run alembic upgrade head
```

### IPFS

For executing PQL definition an IPFS daemon is required. You can start it with:

```
IPFS_PATH=~/.ipfs ipfs daemon &
```

### Ethereum chain

For processing events on Ethereum, a node is required. It can be specified in `.env` file through `WEB3_PROVIDER_URI` variable on the very first rune. For Infura node provide the whole address. Afterwards you can change your chain config in `~/.paralink/chain_config.json` file. Additional EVM chains can be added:

```json
{
	"name": "plasm-local",
	"type": "evm",
	"project": "plasm",
	"url":  "ws://localhost:8545",
	"credentials": {"private_key": "<PRIVATE_KEY>"},
	"tracked_contracts": [<list of contract addresses to listen for events>],
	"oracle_metadata": "<path_to_oracle_abi> | optional"
}
```

### Substrate chain

For processing events on a Substrate parachain add an entry to chain config in `~/.paralink/chain_config.json` file:


```
{
	"name": "dev-canvas",
	"type": "substrate",
	"project": "canvas",
	"url": "ws://127.0.0.1:9944",
	"credentials":{
			"private_key": "<PRIVATE_KEY>",
			"public_key": "<PUBLIC_KEY, different than SS58 ADDRESS>"
	},
	"tracked_contracts": [<list of contract addresses to listen for events>],
	"metadata_file": "<path to ink! oracle metadata.json | optional"
}
```


Note that only Substrate events are currently supported. Soliditiy events from the EVM pallet are not supported at the moment as the event polling API is not implemented yet on the `parity/frontier` project.

The following version of Substrate node was tested:

```
docker run --detach --rm -p 9933:9933 -p 9944:9944 -p 9615:9615 \
					 -v substrate-dev:/substrate parity/substrate:2.0.0-533bbbd --dev --tmp \
					 --unsafe-ws-external --rpc-cors=all --unsafe-rpc-external --rpc-methods=Unsafe \
					 --prometheus-external
```


## Run step by step

If you want to run a background worker to collect on-chain events, see [Event processing](#event-processing).

Alternatively you can disable the background worker by setting the following environment variable to false in the .env file:

```
ENABLE_BACKGROUND_WORKER="False"
```

Running the node is a multistage process:

```
pipenv sync
./paralink-node node start
```

The node will by default listen on port `7424`.

The node exposes two JSON RPC methods, which will execute PQL depending on the location:
 - `execute_pql(pql_json)`: submit PQL JSON in the JSON RPC request (see [simple_get_request.py](examples/simple_get_request.py))
 - `execute_ipfs(ipfs_address, ipfs_hash)`: submit IPFS node address and IPFS hash where your PQL JSON is located (see [examples/ipfs_request.py](examples/ipfs_request.py))

Furthermore see [examples](examples) folder for additional examples on how to use the node directly.

#### Event processing

To start listening for on-chain events start celery workers:

```
docker run -d -p 5672:5672 rabbitmq
pipenv run celery -A src.process.processor worker -l DEBUG -Q collect,execute
```

which spawns two queues for collecting events and executing PQL definitions defined in the events.

Solidity contracts are available [here](https://github.com/paralink-network/solidity-contracts). Start a `ganache-cli` and call:

```
pipenv run brownie run oracle main
```

to deploy the `ParalinkOracle` contracts in the `solidity-contracts` repo.

## Docker run

We suggest using Docker to run the image:

```
docker build -t paralink-node .
docker run -it -p 7424:7424 paralink-node ./paralink-node node start --host 0.0.0.0
```

`docker-compose.yml` file is also available.


## Web UI

A Web UI is accessible on [localhost:7424](http://localhost:7424). It lists all your local IPFS files as well as allows you to create your own PQL definitions, test them and save them to IPFS.

## Docs

We use Sphinx to generate docs. To auto generate docs, use:

```
pipenv run sphinx-apidoc -f -o docs/source paranode
cd docs/
pipenv run make html
```

the files will be available under `docs/build/html`.


## Tests

You can run tests with:

```
pipenv run pytest
```

## Pre-commit hooks

We use pre-commit hooks to enforce coding standards. To install pre-commit hooks:

```
pipenv run pre-commit install
```
