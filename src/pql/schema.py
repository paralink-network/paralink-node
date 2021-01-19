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
        "step": {"const", "extract"},
        "method": {"const": "sql.postgres"},
        "uri": {"type": "string"},
        "query": {"type": "string"},
    },
    "required": ["step", "method", "uir", "query"],
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
        }
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
