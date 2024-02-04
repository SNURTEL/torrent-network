from dataclasses import dataclass
from collections import namedtuple
import socket

Peer = namedtuple("Peer", ("address", "availability"))


@dataclass
class File:
    size: int
    file_hash: str
    timeout: int
    peers: list[Peer]


def encode_peers(peers: list[Peer]) -> bytes:
    return b''.join([socket.inet_aton(peer.address) + int.to_bytes(peer.availability, length=1, byteorder='little',
                                                                   signed=False) + b'\0\0\0' for peer in peers])


def decode_peers(peers: bytes) -> list[Peer]:
    return [Peer(address=socket.inet_ntoa(peer_bytes[:4]),
                 availability=int.from_bytes(peer_bytes[4:5], byteorder='little', signed=False)) for peer_bytes in
            [peers[i:i + 8] for i in range(0, len(peers), 8)]]


if __name__ == "__main__":
    peers = [Peer(
        address="0.0.0.0",
        availability=1
    ), Peer(
        address="1.1.1.1",
        availability=2
    )]

    print(peers)
    peers_bytes = encode_peers(peers)
    print(peers_bytes)
    peers = decode_peers(peers_bytes)
    print(peers)
