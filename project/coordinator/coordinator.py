import random
import socket
import sys
import asyncio
import time
from hashlib import sha256

from project.messages.pack import unpack, pack
from project.messages.body import MsgType, ErrorCode, PEERS_body, ERROR_body, REPRT_body
from project.coordinator.data_classes import File, Peer, encode_peers, decode_peers

hostname = socket.gethostname()
HOST_DEFAULT = socket.gethostbyname(hostname)
files = list()
file_timeout = 5 * 60  # in seconds


async def accept_connections():
    host = HOST_DEFAULT
    port = 8000

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST_DEFAULT, port))
        server_socket.listen(5)

        print(f"Server listening on {host}:{port}")

        loop = asyncio.get_event_loop()
        start_time = time.time()

        while True:
            client_socket, addr = await loop.sock_accept(server_socket)
            check_validity(time.time() - start_time)
            start_time = time.time()
            print(f"Connection from {addr}")

            while msg_type_byte := await loop.sock_recv(client_socket, 1):
                match int.from_bytes(msg_type_byte, byteorder='little', signed=False):
                    case MsgType.APEER.value:
                        data = await loop.sock_recv(client_socket, 71)
                        await process_APEER(msg_type_byte + data, loop, client_socket)
                    case MsgType.REPRT.value:
                        data = await loop.sock_recv(client_socket, 43)
                        await process_REPRT(msg_type_byte + data, client_socket)

            client_socket.close()



def check_validity(timeout: float):
    valid_files = []
    global files

    for file in files:
        file.timeout -= timeout
        if file.timeout > 0:
            valid_files.append(file)
    files = valid_files
    print(f"Files: {files}")


def find_file(hash: str) -> File | None:
    for file in files:
        if file.file_hash == hash:
            return file
    return None


def create_file(body: REPRT_body, peer_name: str) -> None:
    peers = [Peer(
        address=peer_name,
        availability=int(body.availability)
    )]
    file = File(
        size=int(body.file_size),
        file_hash=body.file_hash.decode("utf-8"),
        timeout=int(file_timeout),
        peers=peers
    )

    files.append(file)


def update_file(file: File, body: REPRT_body, peer_name: str) -> None:
    for peer in file.peers:
        if peer.address == peer_name:
            file.timeout = file_timeout
            file.peers.remove(peer)
            break

    if body.availability != 0:
        peer = Peer(
            address=peer_name,
            availability=body.availability
        )
        file.peers.append(peer)
    else:
        global files
        files = [f for f in files if f.file_hash != file.file_hash]


def create_availability_report(file: File) -> bytes:
    body = PEERS_body(
        msg_type=MsgType.PEERS.value,
        file_hash=str.encode(file.file_hash),
        file_size=file.size,
        num_peers=len(file.peers),
        peers=encode_peers(file.peers)
    )

    return pack(body)


def create_error_msg() -> bytes:
    body = ERROR_body(
        msg_type=MsgType.ERROR.value,
        error_code=ErrorCode.NO_FILE_FOUND.value
    )
    return pack(body)


async def process_APEER(data, loop, client_socket):
    unpacked = unpack(data=data, msg_type=MsgType.APEER)
    requested_file = find_file(unpacked.file_hash.decode("utf-8"))
    try:
        if requested_file is None:
            error_msg = create_error_msg()
            await loop.sock_sendall(sock=client_socket, data=error_msg)
            print("No file found - sent ERROR message")
        else:
            report = create_availability_report(requested_file)
            await loop.sock_sendall(sock=client_socket, data=report)
            print("Sent PEERS")
    except Exception as e:
        print(e)
        await loop.sock_sendall(sock=client_socket, data=pack(ERROR_body(msg_type=MsgType.ERROR.value, error_code=1)))


async def process_REPRT(data, client_socket):
    print("Got REPRT")
    unpacked = unpack(data=data, msg_type=MsgType.REPRT)
    reported_file = find_file(unpacked.file_hash.decode("utf-8"))
    if reported_file is None:
        create_file(unpacked, client_socket.getpeername()[0])
    else:
        update_file(reported_file, unpacked, client_socket.getpeername()[0])


if __name__ == "__main__":
    asyncio.run(accept_connections())
