import base58
import binascii

from brownie import *


def main():
    oracle = ParalinkOracle.deploy({"from": accounts[0]})

    # raise


def create_request():
    oracle = ParalinkOracle.at("0x3194cBDC3dbcd3E11a07892e7bA5c3394048Cc87")
    ipfs_hash = "QmTUFeBdxkGJsvFeTthwrYNwfkNWkE4e5P5f8goPdLoLGc"

    ipfs_bytes32 = ipfs_to_bytes32(ipfs_hash)
    print(ipfs_bytes32)
    tx = oracle.request(
        ipfs_bytes32, accounts[1], oracle.address, 0, 3, "", {"from": accounts[1]}
    )


def _ipfs_to_bytes32(hash_str: str):
    bytes_array = base58.b58decode(hash_str)
    b = bytes_array[2:]
    return binascii.hexlify(b).decode("utf-8")


def ipfs_to_bytes32(ipfs_hash: str) -> str:
    """bytes32 is converted back into Ipfs hash format."""
    ipfs_hash_bytes32 = _ipfs_to_bytes32(ipfs_hash)
    return web3.toBytes(hexstr=ipfs_hash_bytes32)
