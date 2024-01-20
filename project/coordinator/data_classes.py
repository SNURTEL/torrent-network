from dataclasses import dataclass
from collections import namedtuple

Peer = namedtuple("Peer", ("address", "availability"))


@dataclass
class File:
    size: int
    file_hash: str
    timeout: int
    peers: list[Peer]


def encode_peers(peers: list[Peer]) -> str:
    encoded_peers = ""
    for peer in peers:
        encoded_peers += f"{peer.address},{peer.availability};"
    return encoded_peers


def decode_peers(peers: str) -> list[Peer]:
    decoded_peers = list()
    peers_list = peers.split(';')[:-1]
    for peer in peers_list:
        temp = peer.split(',')
        decoded_peers.append(Peer(
            address=temp[0],
            availability=int(temp[1])
        ))
    return decoded_peers


if __name__ == "__main__":
    peers = []
    peers.append(Peer(
        address="0.0.0.0",
        availability=1
    ))
    peers.append(Peer(
        address="1.1.1.1",
        availability=2
    ))

    print(peers)
    peers_str = encode_peers(peers)
    print(peers_str)
    peers = decode_peers(peers_str)
    print(peers)