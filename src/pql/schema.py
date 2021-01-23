from src.config import config

step_extract_http = {
    "type": "object",
    "properties": {
        "step": {"const": "extract"},
        "method": {"enum": ["http.get", "http.post"]},
        "uri": {"type": "string"},
    },
    "required": ["step", "method", "uri"],
    "if": {"properties": {"method": {"const": "http.post"}}},
    "then": {"properties": {"params": {"type": "object"}}, "required": ["params"]},
}

step_extract_sql = {
    "type": "object",
    "properties": {
        "step": {"const": "extract"},
        "method": {"const": "sql.postgres"},
        "uri": {"type": "string"},
        "query": {"type": "string"},
    },
    "required": ["step", "method", "uri", "query"],
}

step_extract_eth = {
    "type": "object",
    "properties": {
        "step": {"const": "extract"},
        "method": {"enum": ["eth.balance", "eth.function"]},
        "address": {"type": "string"},
    },
    "required": ["step", "method", "address"],
    "if": {"properties": {"method": {"const": "eth.balance"}}},
    "then": {
        "properties": {
            "params": {
                "type": "object",
                "properties": {
                    "block": {"oneOf": [{"const": "latest"}, {"type": "integer"}]},
                    "num_confirmations": {"type": "integer"},
                },
                "required": ["block"],
            }
        },
        "required": ["params"],
    },
    "else": {
        "properties": {
            "params": {
                "type": "object",
                "properties": {
                    "function": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}},
                    "num_confirmations": {"type": "integer"},
                    "block": {"oneOf": [{"const": "latest"}, {"type": "integer"}]},
                },
                "required": ["function", "args", "block"],
            },
        },
        "required": ["params"],
    },
}

step_traverse = {
    "type": "object",
    "properties": {
        "method": {"const": "json"},
        "params": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["method", "params"],
}

step_get_index = {
    "type": "object",
    "properties": {"step": {"const": "get_index"}, "params": {"type": "integer"}},
    "required": ["step", "params"],
}

step_math = {
    "type": "object",
    "properties": {
        "step": {"const": "math"},
        "method": {"enum": ["mul", "add", "sub", "div"]},
        "params": {"type": "number"},
        "direction": {"const": {"reverse"}},
    },
    "required": ["step", "method", "params"],
}

step_query_sql = {
    "type": "object",
    "properties": {
        "step": {"const": "query.sql"},
        "method": {"enum": ["json", "list", None]},
        "query": {"type": "string"},
        "result": {"type": "boolean"},
    },
    "required": ["step", "query", "method"],
}

custom_steps = [
    custom_method.SCHEMA for custom_method in config.PQL_CUSTOM_METHODS.values()
]

source = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "pipeline": {
            "type": "array",
            "items": {
                "oneOf": [
                    step_extract_http,
                    step_extract_sql,
                    step_extract_eth,
                    step_traverse,
                    step_get_index,
                    step_math,
                    step_query_sql,
                ]
                + custom_steps
            },
        },
    },
    "required": ["name", "pipeline"],
}

aggregate = {
    "type": "object",
    "properties": {"method": {"enum": ["mean", "median", "max", "min", "query.sql"]}},
    "required": ["method"],
    "if": {"properties": {"method": {"const": "query.sql"}}},
    "then": {
        "properties": {
            "params": {"type": "array", "items": {"enum": ["json", "list", None]}},
            "query": {"type": "string"},
            "result": {"const": True},
        },
        "required": ["params", "query", "result"],
    },
}

pql = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "psql_version": {"type": "string"},
        "sources": {"type": "array", "items": source},
        "aggregate": aggregate,
    },
    "required": ["name", "psql_version", "sources"],
}
