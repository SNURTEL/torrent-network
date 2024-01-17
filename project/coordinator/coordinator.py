import socket
import sys
import asyncio
from typing import Any

from project.messages.pack import unpack, pack
from project.messages.body import MsgType, ErrorCode, PEERS_body, ERROR_body
from project.coordinator.data_classes import File

HOST_DEFAULT = "localhost"
files = list()


async def accept_connections():
    if len(sys.argv) < 3:
        host = HOST_DEFAULT
        port = 8000
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST_DEFAULT, port))
        server_socket.listen(5)

        print(f"Server listening on {host}:{port}")

        loop = asyncio.get_event_loop()

        while True:
            client_socket, addr = await loop.sock_accept(server_socket)
            print(f"Connection from {addr}")

            data = await loop.sock_recv(client_socket, 72)

            # todo: find a way to just call unpack without the match statement
            match int(data[0]):
                case MsgType.APEER.value:
                    unpacked = unpack(data=data, msg_type=MsgType.APEER)
                    requested_file = find_file(unpacked.file_hash)
                    if requested_file is None:
                        error_msg = create_error_msg()
                        await loop.sock_sendall(sock=client_socket, data=error_msg)
                        print("No file found - sent ERROR message")
                    else:
                        report = create_availability_report(requested_file)
                        await loop.sock_sendall(sock=client_socket, data=report)
                        print("Sent PEERS")
                case MsgType.REPRT.value:
                    unpacked = unpack(data=data, msg_type=MsgType.REPRT)


def find_file(hash: str) -> File | None:
    for file in files:
        if file.file_hash == hash:
            return file
    return None


def create_availability_report(file: File) -> bytes:
    body = PEERS_body(
        msg_type=MsgType.PEERS.value,
        chunk_num=file.chunks_num,
        chunk_hashes=file.chunk_hashes,
        file_hash=file.file_hash,
        file_size=file.size,
        peers=file.peers
    )

    return pack(body)


def create_error_msg() -> bytes:
    body = ERROR_body(
        msg_type=MsgType.ERROR.value,
        error_code=ErrorCode.NO_FILE_FOUND.value
    )

    return pack(body)


if __name__ == "__main__":
    asyncio.run(accept_connections())
