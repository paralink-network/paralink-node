![](https://paralink.network/images/logo-sm-home.png)

# Overview ![paralink-node CI](https://github.com/paralink-network/paralink-node/workflows/paralink-node%20CI/badge.svg)

Paralink Node is responsible for executing ETL pipelines and PQL queries. The results are relayed to
all supported chains via callbacks. Paralink Node is also a dependency to the on-chain [runtime](https://github.com/paralink-network/paralink-substrate).


## Quick start

Make sure you downloaded all of git submodules, either with `git clone --recurse-submodules` or if you already cloned the repo run:

```
git submodule init 
git submodule update
```

Paralink node uses local configuration stored in `~/.paralink`. Create the directory with 

```
mkdir ~/.paralink
```

This is where all node data will be stored.

Before running the node, please setup your `.env`. Copy the `.env.template` file to `.env` and modify the variables. 

To run the node we recommend using `docker-compose`. For your convenience you can run the commands through `make`:

```
make up
```

The node will be available at [localhost:7245](http://localhost:7425). The above command will deploy PostgreSQL, IPFS, RabbitMQ message broker, background Celery worker as well as `nginx` server serving `paralink-ui` React app.

Whenever you want to shut down the node run:

```
make down
```

If you make any changes to the code or configuration, you have to rebuild the containers with:

```
make build
```

In case you do not want to run the UI (e.g. developing frontend), use:

```
make backend
```

## Configuration

### Chain configuration
On the first run a default chain config will be created (`~/.paralink/chain_config.json`). Modify it to include your own set of chains. If you run a local chain node, do not forget to modify the `docker-compose.yml` file to either include the chain container or use `network: host` to use the local chain. 

#### Ethereum chain

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

#### Substrate chain

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


Note that only Substrate events are currently supported. Solidity events from the EVM pallet are not supported at the moment as the event polling API is not implemented yet on the `parity/frontier` project.

The following version of Substrate node was tested:

```
docker run --detach --rm -p 9933:9933 -p 9944:9944 -p 9615:9615 \
					 -v substrate-dev:/substrate parity/substrate:2.0.0-533bbbd --dev --tmp \
					 --unsafe-ws-external --rpc-cors=all --unsafe-rpc-external --rpc-methods=Unsafe \
					 --prometheus-external
```


## Run step by step

In case you want to run the node without the container, there is a couple of dependencies to be installed. The node requires a running PostgreSQL, IPFS API service and a RabbitMQ message broker. The node will not start if any of them is missing.

First sync up the python dependencies:

```
pipenv sync
```

### PostgreSQL DB

Relevant DB `.env` variables:

```
DATABASE_NAME=paralink_node
DATABASE_HOST=psql
DATABASE_USER=paralink
DATABASE_PASSWORD=p4r4link
```

Migrate the DB with:
```
pipenv run alembic upgrade head
```

### IPFS

For executing PQL jobs an IPFS daemon is required. Follow the instructions on [their site](https://docs.ipfs.io/install/) to get it running. To run the daemon you can use:

```
IPFS_PATH=~/.ipfs ipfs daemon &
```

Set the `.env` variable `IPFS_API_SERVER_ADDRESS` to the IPFS API service:

```
IPFS_API_SERVER_ADDRESS=/ip4/127.0.0.1/tcp/5001
```

### Event processing

For dispatching events, we need RabbitMQ. We use `docker` to deploy it:

```
docker run -d -p 5672:5672 rabbitmq
```

To start listening for on-chain events start celery workers:

```
pipenv run celery -A src.process.processor worker -l DEBUG -Q collect,execute
```

which spawns two queues for collecting events and executing PQL definitions defined in the events.

Alternatively you can disable the background worker by setting the following environment variable to `False` in the [.env](.env.template) file:

```
ENABLE_BACKGROUND_WORKER=False
```

### Running the node

To run the node, use:

```
./paralink-node node start
```

The node will by default listen on port `7424`.

The node exposes two JSON RPC methods, which will execute PQL depending on the location:
 - `execute_pql(pql_json)`: submit PQL JSON in the JSON RPC request (see [simple_get_request.py](examples/simple_get_request.py))
 - `execute_ipfs(ipfs_address, ipfs_hash)`: submit IPFS node address and IPFS hash where your PQL JSON is located (see [examples/ipfs_request.py](examples/ipfs_request.py))

Furthermore see [examples](examples) folder for additional examples on how to use the node directly.


### React UI

To run the React UI, follow the instructions in the [paralink-ui repo](https://github.com/paralink-network/paralink-ui). It lists all your local IPFS files as well as allows you to create your own PQL definitions, test them and save them to IPFS.


### Oracles


#### Solidity

Solidity  contracts are available [in soliditiy-contracts](https://github.com/paralink-network/solidity-contracts). Start a `ganache-cli` and call:

```
pipenv run brownie run oracle main
```

to deploy the `ParalinkOracle` contracts in the `solidity-contracts` repo.

#### Substrate

Substrate contracts are available in the [ink-contracts repo](https://github.com/paralink-network/ink-contracts).


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
