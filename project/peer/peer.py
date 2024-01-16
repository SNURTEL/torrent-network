import socket
import asyncio
from hashlib import sha256

from project.messages.body import MsgType, GCHNK_body, SCHNK_body
from project.messages.pack import pack, unpack

socket.socketpair()

CHUNK_SIZE = 1024


async def download_chunk(sock: socket.socket, file_hash: bytes, chunk_num: bytes) -> bytes:
    loop = asyncio.get_event_loop()

    gchnk_bytes = pack(GCHNK_body(msg_type=MsgType.GCHNK, file_hash=file_hash, chunk_num=chunk_num))
    await loop.sock_sendall(sock=sock, data=gchnk_bytes)
    prefix = await loop.sock_recv(sock=sock, nbytes=72)  # todo magic numbers - this is SCHNK size without content
    unpacked = unpack(data=prefix, msg_type=MsgType.SCHNK)

    assert unpacked.msg_type == MsgType.SCHNK
    assert unpacked.chunk_num == chunk_num
    assert unpacked.file_hash == file_hash

    if (decoded := unpacked.chunk_num.decode()) != (calculated := sha256(unpacked.chunk_hash).hexdigest()):
        raise ValueError(f"Chunk ${unpacked.chunk_num} hash not matching: got {decoded}, expected {calculated}")

    return unpacked.content


async def download_chunks(sock: socket.socket, file_hash: bytes, chunk_nums: list[bytes]) -> list[bytes]:
    chunks = []
    for chunk_num in chunk_nums:
        try:
            chunks.append(await download_chunk(sock, file_hash=file_hash, chunk_num=chunk_num))
        except ValueError as e:
            print(f"Failed to download chunk {chunk_num}")
            chunks.append(None)

    return chunks
