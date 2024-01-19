import socket
import sys
import asyncio

from project.messages.pack import unpack, pack
from project.messages.body import MsgType, ErrorCode, PEERS_body, ERROR_body, REPRT_body
from project.coordinator.data_classes import File, Peer, encode_peers, decode_peers

HOST_DEFAULT = "localhost"
files = list()
file_timeout = 5 * 6  # in seconds
check_interval = 6


async def main():
    tasks = [asyncio.create_task(do_stuff_every_x_seconds(check_interval)), asyncio.create_task(accept_connections())]

    await asyncio.gather(*tasks)


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
            if data:
                match int(data[0]):
                    case MsgType.APEER.value:
                        await process_APEER(data, loop, client_socket)
                    case MsgType.REPRT.value:
                        await process_REPRT(data, client_socket)

            print(f"Files: {files}")


async def do_stuff_every_x_seconds(timeout):
    while True:
        await asyncio.sleep(timeout)
        await check_validity(timeout)


async def check_validity(timeout: int):
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


def create_file(body: REPRT_body, peer_name: str):
    peers = [Peer(address=peer_name, availability=int(body.availability))]
    file = File(
        size=int(body.file_size), file_hash=body.file_hash.decode("utf-8"), timeout=int(file_timeout), peers=peers
    )

    files.append(file)


def update_file(file: File, body: REPRT_body, peer_name: str):
    for peer in file.peers:
        if peer.address == peer_name:
            file.timeout = file_timeout
            file.peers.remove(peer)
            break

    peer = Peer(address=peer_name, availability=body.availability)
    file.peers.append(peer)


def create_availability_report(file: File) -> bytes:
    body = PEERS_body(
        msg_type=MsgType.PEERS.value,
        file_hash=str.encode(file.file_hash),
        file_size=file.size,
        peers=str.encode(encode_peers(file.peers)),
    )

    return pack(body)


def create_error_msg() -> bytes:
    body = ERROR_body(msg_type=MsgType.ERROR.value, error_code=ErrorCode.NO_FILE_FOUND.value)

    return pack(body)


async def process_APEER(data, loop, client_socket):
    unpacked = unpack(data=data, msg_type=MsgType.APEER)
    requested_file = find_file(unpacked.file_hash.decode("utf-8"))
    if requested_file is None:
        error_msg = create_error_msg()
        await loop.sock_sendall(sock=client_socket, data=error_msg)
        print("No file found - sent ERROR message")
    else:
        report = create_availability_report(requested_file)
        await loop.sock_sendall(sock=client_socket, data=report)
        print("Sent PEERS")


async def process_REPRT(data, client_socket):
    unpacked = unpack(data=data, msg_type=MsgType.REPRT)
    reported_file = find_file(unpacked.file_hash.decode("utf-8"))
    if reported_file is None:
        create_file(unpacked, client_socket.getpeername()[0])
    else:
        update_file(reported_file, unpacked, client_socket.getpeername()[0])


if __name__ == "__main__":
    asyncio.run(main())
