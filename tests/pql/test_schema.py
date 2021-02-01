import pytest

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from src.pql.schema import (
    aggregate,
    pql,
    source,
    step_extract_eth,
    step_extract_http,
    step_extract_sql,
    step_get_index,
    step_query_sql,
    step_traverse,
)


def test_schema_step_extract_http_post() -> None:
    instance = {
        "step": "extract",
        "method": "http.post",
        "uri": "https://test",
        "params": {"key": "value"},
    }
    validate(instance, step_extract_http)


def test_schema_step_extract_http_post_no_params() -> None:
    instance = {
        "step": "extract",
        "method": "http.post",
        "uri": "https://test",
    }
    with pytest.raises(ValidationError):
        validate(instance, step_extract_http)


def test_schema_step_extract_eth_function() -> None:
    instance = {
        "step": "extract",
        "method": "eth.function",
        "address": "0xBb2b8038a1640196FbE3e38816F3e67Cba72D940",
        "chain_id": 1,
        "params": {
            "function": "balanceOf(address)",
            "args": ["0x9b89202Fc32c294Df4B2b52830fF40B3EC0F0369"],
            "block": 11514560,
        },
    }
    validate(instance, step_extract_eth)


def test_schema_step_extract_eth_function_no_block() -> None:
    instance = {
        "step": "extract",
        "method": "eth.function",
        "address": "0xBb2b8038a1640196FbE3e38816F3e67Cba72D940",
        "chain_id": 1,
        "params": {
            "function": "balanceOf(address)",
            "args": ["0x9b89202Fc32c294Df4B2b52830fF40B3EC0F0369"],
        },
    }
    with pytest.raises(ValidationError):
        validate(instance, step_extract_eth)


def test_schema_step_extract_eth_balance() -> None:
    instance = {
        "step": "extract",
        "method": "eth.balance",
        "address": "0x9b89202Fc32c294Df4B2b52830fF40B3EC0F0369",
        "params": {"block": "latest", "num_confirmations": 30},
        "chain_id": 1,
    }
    validate(instance, step_extract_eth)


def test_schema_step_extract_sql_postgres() -> None:
    instance = {
        "step": "extract",
        "method": "sql.postgres",
        "uri": "postgres://user:password@localhost/my_database_name",
        "query": "select * FROM (VALUES ('BTC', 20000)) AS t (symbol, price);",
    }
    validate(instance, step_extract_sql)


def test_schema_step_traverse() -> None:
    instance = {
        "step": "traverse",
        "method": "json",
        "params": ["bitcoin", "usd"],
    }
    validate(instance, step_traverse)


def test_schema_step_get_index() -> None:
    instance = {
        "step": "get_index",
        "params": 6,
    }
    validate(instance, step_get_index)


def test_schema_step_query_sql() -> None:
    instance = {
        "step": "query.sql",
        "method": "json",
        "query": "SELECT `bitcoin.usd` FROM response",
        "result": True,
    }
    validate(instance, step_query_sql)


def test_schema_source() -> None:
    instance = {
        "name": "Bitcoin price CoinGecko",
        "pipeline": [
            {
                "step": "extract",
                "method": "http.get",
                "uri": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            },
            {
                "step": "traverse",
                "method": "json",
                "params": ["bitcoin", "usd"],
            },
        ],
    }
    validate(instance, source)


def test_schema_aggregate() -> None:
    instance_1 = {"method": "mean"}
    validate(instance_1, aggregate)
    instance_2 = {
        "method": "query.sql",
        "params": ["json", "list", "json"],
        "query": "SELECT AVG(price) FROM (SELECT `bitcoin.usd` AS price FROM result_0 UNION SELECT `6` AS price FROM result_1 UNION SELECT `bpi.USD.rate_float` AS price FROM result_2)",
        "result": True,
    }
    validate(instance_2, aggregate)


def test_schema_pql() -> None:
    instance = {
        "name": "Aggregate HTTP requests",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Bitcoin price CoinGecko",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
                    }
                ],
            },
            {
                "name": "Bitcoin price Bitfinex",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api-pub.bitfinex.com/v2/ticker/tBTCUSD",
                    }
                ],
            },
            {
                "name": "Bitcoin price CoinDesk",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://api.coindesk.com/v1/bpi/currentprice.json",
                    }
                ],
            },
        ],
        "aggregate": {
            "method": "query.sql",
            "params": ["json", "list", "json"],
            "query": "SELECT AVG(price) FROM (SELECT `bitcoin.usd` AS price FROM result_0 UNION SELECT `6` AS price FROM result_1 UNION SELECT `bpi.USD.rate_float` AS price FROM result_2)",
            "result": True,
        },
    }
    validate(instance, pql)
