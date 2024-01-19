import asyncio, socket
from hashlib import sha256

from project.messages.pack import pack, unpack
from project.messages.body import SCHNK_body, MsgType

CHUNK_SIZE = 1024


async def _handle_client(client):
    loop = asyncio.get_event_loop()

    while msg_type_byte := await loop.sock_recv(client, 1):
        msg_type = MsgType(int.from_bytes(msg_type_byte, signed=False, byteorder='little'))
        match msg_type:
            case MsgType.GCHNK:
                rest = await loop.sock_recv(client, 72 + CHUNK_SIZE - 1)
                msg = unpack(msg_type_byte + rest, MsgType.GCHNK)
                print(f"Got GCHNK, chunk_num={msg.chunk_num}")

                with open("source.jpg", mode='rb') as fp:
                    fp.seek(msg.chunk_num * CHUNK_SIZE)
                    response_content = fp.read(CHUNK_SIZE)
                    if len(response_content) < CHUNK_SIZE:
                        response_content += b'\0' * (CHUNK_SIZE - len(response_content))

                response = pack(SCHNK_body(
                    msg_type=MsgType.SCHNK.value,
                    file_hash=msg.file_hash,
                    chunk_num=msg.chunk_num,
                    chunk_hash=str.encode(sha256(response_content).hexdigest()),
                    content=response_content
                ))
                await loop.sock_sendall(client, response)

            case _:
                raise ValueError("Unknown message type")


async def handle_client(client):
    try:
        await _handle_client(client)
    finally:
        client.close()
        print("Close socket")


async def run_server(port = 8888):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', 8888))
        server.listen(8)
        server.setblocking(False)

        loop = asyncio.get_event_loop()

        while True:
            client, _ = await loop.sock_accept(server)
            loop.create_task(handle_client(client))
    finally:
        server.shutdown(0)
        server.close()


if __name__ == '__main__':
    asyncio.run(run_server())
