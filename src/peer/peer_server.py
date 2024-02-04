import json
import random
import sys
import asyncio, socket
from hashlib import sha256

from src.messages.pack import pack, unpack
from src.messages.body import SCHNK_body, MsgType, CHNKS_body, ERROR_body, ErrorCode
from src.peer.reporting import report_availability_periodically, get_resource_dir_hashes

CHUNK_SIZE = 1024

RESOURCE_DIR = "resources"


async def _handle_client(client, client_addr):
    hash_file_mapping = {}

    def refresh_hash_file_mapping():
        nonlocal hash_file_mapping
        hash_file_mapping = {v: k for k, v in get_resource_dir_hashes().items()}

    def get_file_from_hash(file_hash: str) -> str:
        file = hash_file_mapping.get(file_hash)
        if not file:
            refresh_hash_file_mapping()
            file = hash_file_mapping.get(file_hash)
        return file

    refresh_hash_file_mapping()

    loop = asyncio.get_event_loop()

    while msg_type_byte := await loop.sock_recv(client, 1):
        msg_type = MsgType(int.from_bytes(msg_type_byte, signed=False, byteorder='little'))
        match msg_type:
            case MsgType.GCHNK:
                rest = await loop.sock_recv(client, 39)
                msg = unpack(msg_type_byte + rest, MsgType.GCHNK)
                file_hash = msg.file_hash.decode()
                file = get_file_from_hash(file_hash)

                if not file:
                    print(f"Got GCHNK from {client_addr} chunk {msg.chunk_num} of unknown file ({msg.file_hash})")
                    response = pack(ERROR_body(
                        msg_type=MsgType.ERROR.value,
                        error_code=ErrorCode.NO_FILE_FOUND.value
                    ))
                else:
                    print(f"Got GCHNK from {client_addr} chunk {msg.chunk_num} of {file}")
                    with open(RESOURCE_DIR + '/' + file, mode='rb') as fp:
                        fp.seek(msg.chunk_num * CHUNK_SIZE)
                        response_content = fp.read(CHUNK_SIZE)
                        if len(response_content) < CHUNK_SIZE:
                            response_content += b'\0' * (CHUNK_SIZE - len(response_content))

                    response = pack(SCHNK_body(
                        msg_type=MsgType.SCHNK.value,
                        file_hash=msg.file_hash,
                        chunk_num=msg.chunk_num,
                        chunk_hash=str.encode(sha256(response_content).hexdigest()[:32]),
                        content=response_content
                    ))

                await loop.sock_sendall(client, response)

            case MsgType.ACHNK:
                rest = await loop.sock_recv(client, 36 - 1)
                msg = unpack(msg_type_byte + rest, MsgType.ACHNK)

                file_hash = msg.file_hash.decode()
                file = get_file_from_hash(file_hash)

                if not file:
                    print(f"Got ACHNK from {client_addr} for unknown file ({file_hash})")
                    response = pack(ERROR_body(
                        msg_type=MsgType.ERROR.value,
                        error_code=ErrorCode.NO_FILE_FOUND.value
                    ))
                else:
                    print(f"Got ACHNK from {client_addr} for {file}")
                    with open(f'{RESOURCE_DIR}/{file}.fileinfo', mode='rb') as fp:
                        fileinfo = json.load(fp)
                    num_chunks = fileinfo['num_chunks']
                    avail = random.sample(list(range(num_chunks)), k=num_chunks // 2)

                    response = pack(CHNKS_body(
                        msg_type=MsgType.CHNKS.value,
                        file_hash=msg.file_hash,
                        num_chunks=num_chunks // 2,
                        availability=b''.join(
                            [int.to_bytes(num, length=4, byteorder='little', signed=False) for num in avail])
                    ))
                await loop.sock_sendall(client, response)

            case _:
                raise ValueError("Unknown message type")


async def handle_client(client, client_addr):
    try:
        await _handle_client(client, client_addr)
    finally:
        client.close()
        print("Close socket")


async def chunk_server(addr: str, port_num: int):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((addr, port_num))
        server.listen(8)
        server.setblocking(False)

        loop = asyncio.get_event_loop()

        while True:
            client, client_addr = await loop.sock_accept(server)
            loop.create_task(handle_client(client, client_addr))
    finally:
        server.shutdown(0)
        server.close()


async def client_listener_server(sock_path: str):
    server = None

    async def handle_req(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        msg_byte = await reader.readexactly(1)
        writer.write(msg_byte)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

        with open("server.log", mode='a') as fp:
            fp.writelines(f"got {msg_byte}")

        if msg_byte != b'\x00':
            with open("server.log", mode='a') as fp:
                fp.writelines(f"try stop")
            server.close()
            await server.wait_closed()


    server = await asyncio.start_unix_server(handle_req, path=sock_path)
    async with server:
         await server.serve_forever()

    with open("server.log", mode='a') as fp:
        fp.writelines(f"stop server")



async def run_peer_server(addr: str, port: int, reporting_interval_seconds: int, client_comm_socket_path: str):
    print("Up & running")

    done, pending = await asyncio.wait([
        asyncio.create_task(chunk_server(addr, port)),
        asyncio.create_task(report_availability_periodically(reporting_interval_seconds)),
        asyncio.create_task(client_listener_server(client_comm_socket_path))
    ], return_when="FIRST_COMPLETED")

    for coro in pending:
        if not coro.cancelled():
            coro.cancel()

    with open("server.log", mode='w') as fp:
        fp.write("server exited")
