chain = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "maxLength": 42},
        "chain_type": {"enum": ["evm", "substrate"]},
        "active": {"type": "boolean"},
        "url": {"type": "string"},
    },
    "required": ["name", "chain_type", "active", "url"],
}

contract_oracle = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "maxLength": 42},
        "active": {"type": "boolean"},
        "chain": {"type": "string", "maxLength": 42},
    },
    "required": ["id", "active", "chain"],
}
