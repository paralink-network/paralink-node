import base58
import binascii


def ipfs_to_bytes32(hash_str: str):
    """Convert IPFS hash to bytes32 type."""
    bytes_array = base58.b58decode(hash_str)
    return bytes_array[2:]


def bytes32_to_ipfs(bytes_array):
    """Convert bytes32 type to IPFS hash."""
    merge = b"\x12\x20" + bytes_array
    return base58.b58encode(merge).decode("utf-8")
