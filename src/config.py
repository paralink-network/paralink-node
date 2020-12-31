from os import getenv
from dotenv import load_dotenv

from src.pql.handlers.rest_api_handler import RestApiHandler

__version__ = "0.1.0"

# Load the main configuration file
load_dotenv(".env")


class Config:
    DEBUG = False
    TESTING = False

    # Ethereum
    ETHERSCAN_KEY = getenv("ETHERSCAN_KEY")
    GETH_HTTP_RPC = getenv("GETH_HTTP_RPC", "http://localhost:8745")
    IPFS_API_SERVER_ADDRESS = getenv("IPFS_API_SERVER_ADDRESS")
    WEB3_PROVIDER_URI = getenv("WEB3_PROVIDER_URI")

    DATABASE_URL = getenv("DATABASE_URL")

    # Default number of confirmations for ETH finality
    DEFAULT_NUM_CONFIRMATIONS = 40

    TEMPLATE_PQL_DEFINITION = {
        "name": "My job name",
        "psql_version": "0.1",
        "sources": [
            {
                "name": "Pipeline 1 name",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://my-crypto-api.com/tickers",
                    },
                ],
            },
            {
                "name": "Pipeline 2 name",
                "pipeline": [
                    {
                        "step": "extract",
                        "method": "http.get",
                        "uri": "https://my-crypto-api.com/tickers",
                    },
                ],
            },
        ],
        "aggregate": {"method": "mean"},
        "callback": [
            {
                "type": "chain.eth",
                "params": {
                    "address": "<ORACLE ETH ADDRESS>",
                    "function": "fulfillRequest",
                    "args": [],
                },
            },
            {
                "type": "chain.plasm",
                "params": {
                    "address": "<ORACLE PLASM ADDRESS>",
                    "function": "fulfillRequest",
                    "args": [],
                },
            },
        ],
    }

    # User defined custom functions
    PQL_CUSTOM_METHODS = {
        # "my_add": lambda step, index, pipeline: pipeline.get_value_for_step(index - 1) + step["params"]
    }

    ORACLE_CONTRACT_ABI = [
        {
            "inputs": [],
            "name": "constructor",
            "stateMutability": "nonpayable",
            "type": "constructor",
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "previousOwner",
                    "type": "address",
                },
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "newOwner",
                    "type": "address",
                },
            ],
            "name": "OwnershipTransferred",
            "type": "event",
        },
        {
            "anonymous": False,
            "inputs": [
                {
                    "indexed": True,
                    "internalType": "bytes32",
                    "name": "ipfsHash",
                    "type": "bytes32",
                },
                {
                    "indexed": True,
                    "internalType": "address",
                    "name": "requester",
                    "type": "address",
                },
                {
                    "indexed": True,
                    "internalType": "bytes32",
                    "name": "requestId",
                    "type": "bytes32",
                },
                {
                    "indexed": False,
                    "internalType": "address",
                    "name": "callbackAddress",
                    "type": "address",
                },
                {
                    "indexed": False,
                    "internalType": "bytes4",
                    "name": "_callbackFunctionId",
                    "type": "bytes4",
                },
                {
                    "indexed": False,
                    "internalType": "uint256",
                    "name": "expiration",
                    "type": "uint256",
                },
                {
                    "indexed": False,
                    "internalType": "bytes",
                    "name": "data",
                    "type": "bytes",
                },
            ],
            "name": "Request",
            "type": "event",
        },
        {
            "inputs": [],
            "name": "EXPIRY_TIME",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "owner",
            "outputs": [{"internalType": "address", "name": "", "type": "address"}],
            "stateMutability": "view",
            "type": "function",
        },
        {
            "inputs": [],
            "name": "renounceOwnership",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "bytes32", "name": "_ipfsHash", "type": "bytes32"},
                {"internalType": "address", "name": "_sender", "type": "address"},
                {
                    "internalType": "address",
                    "name": "_callbackAddress",
                    "type": "address",
                },
                {
                    "internalType": "bytes4",
                    "name": "_callbackFunctionId",
                    "type": "bytes4",
                },
                {"internalType": "uint256", "name": "_nonce", "type": "uint256"},
                {"internalType": "bytes", "name": "_data", "type": "bytes"},
            ],
            "name": "request",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "_node", "type": "address"},
                {"internalType": "bool", "name": "_allowed", "type": "bool"},
            ],
            "name": "setAuthorizedNode",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
        {
            "inputs": [
                {"internalType": "address", "name": "newOwner", "type": "address"}
            ],
            "name": "transferOwnership",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function",
        },
    ]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
