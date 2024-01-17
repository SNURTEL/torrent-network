from dataclasses import dataclass


@dataclass
class Peer:
    address: str
    mask: str
    availability: int


@dataclass
class File:
    name: str
    size: int
    file_hash: str
    chunks_num: int
    chunk_hashes: list[str]
    peers: list[Peer]
