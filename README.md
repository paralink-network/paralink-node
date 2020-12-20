![](https://paralink.network/images/logo-sm-home.png)

Paralink Node is responsible for executing ETL pipelines and PQL queries. The results are relayed to
all supported chains via callbacks. Paralink Node is also a dependency to the on-chain [runtime](https://github.com/paralink-network/paralink-substrate).

## Configure
Before running the node, please inspect `.env`.

## Run

We suggest using Docker to run the image:

```
docker build -t paralink-node .
docker run -it -p 7424:7424 paralink-node ./paralink-node -H 0.0.0.0

```

Otherwise you can build the node yourself:

```
pipenv sync
./paralink-node
```

The node will by default listen on port `7424`, where you can submit your JSON RPC queries through the `execute_pql` method. See [examples](examples) folder for some examples on how to use the node (e.g. simple HTTP GET request can be seen in [simple_get_request.py](examples/simple_get_request.py)).


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

