import pytest

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from src.pql.schema import step_extract_eth, step_extract_http


def test_schema_step_extract_http_post() -> None:
    step_extract_post = {
        "step": "extract",
        "method": "http.post",
        "uri": "https://test",
        "params": {"key": "value"},
    }
    validate(step_extract_post, step_extract_http)


def test_schema_step_extract_http_post_no_params() -> None:
    step_extract_post_no_params = {
        "step": "extract",
        "method": "http.post",
        "uri": "https://test",
    }
    with pytest.raises(ValidationError):
        validate(step_extract_post_no_params, step_extract_http)


def test_schema_step_extract_eth_function() -> None:
    step_extract_eth_function = {
        "step": "extract",
        "method": "eth.function",
        "address": "0xBb2b8038a1640196FbE3e38816F3e67Cba72D940",
        "params": {
            "function": "balanceOf(address)",
            "args": ["0x9b89202Fc32c294Df4B2b52830fF40B3EC0F0369"],
            "block": 11514560,
        },
    }
    validate(step_extract_eth_function, step_extract_eth)


def test_schema_step_extract_eth_balance() -> None:
    step_extract_eth_balance = {
        "step": "extract",
        "method": "eth.balance",
        "address": "0x9b89202Fc32c294Df4B2b52830fF40B3EC0F0369",
        "params": {"block": "latest", "num_confirmations": 30},
    }

    validate(step_extract_eth_balance, step_extract_eth)
