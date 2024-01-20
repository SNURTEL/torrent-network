import socket
import asyncio
import math
import shutil
import os
from hashlib import sha256

from project.messages.body import MsgType, GCHNK_body
from project.messages.pack import pack, unpack

socket.socketpair()

CHUNK_SIZE = 1024


async def download_chunk(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        file_hash: str,
        chunk_num: int
) -> bytes:
    file_hash_bytes = str.encode(file_hash)
    gchnk_bytes = pack(GCHNK_body(msg_type=MsgType.GCHNK.value, file_hash=file_hash_bytes,
                                  chunk_num=chunk_num))
    writer.write(gchnk_bytes)
    await writer.drain()
    prefix = await reader.readexactly(n=72 + CHUNK_SIZE)  # todo magic numbers - this is SCHNK size without content
    unpacked = unpack(data=prefix, msg_type=MsgType.SCHNK)
    assert unpacked.msg_type == MsgType.SCHNK.value
    assert unpacked.chunk_num == chunk_num
    assert unpacked.file_hash == file_hash_bytes

    if (decoded := unpacked.chunk_hash) != (calculated := str.encode(sha256(unpacked.content).hexdigest()[:32])):
        raise ValueError(f"Chunk ${unpacked.chunk_num} hash not matching: got {decoded}, expected {calculated[:32]}")

    return unpacked.content


async def download_chunks(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        file_hash: str, chunk_nums:
        list[int]
) -> list[bytes]:
    chunks = []
    for chunk_num in chunk_nums:
        try:
            chunks.append(await download_chunk(reader=reader, writer=writer, file_hash=file_hash, chunk_num=chunk_num))
        except ValueError as e:
            print(f"Failed to download chunk {chunk_num}:\n{repr(e)}")
            chunks.append(None)

    return chunks


async def download_file(hash: str, size: int, out_name: str):
    partial_file = f"{out_name}.partial"

    with open(partial_file, "wb") as fp:
        fp.truncate(size)

    async def download_and_save_chunk(
            chunk_num: int,
            chunk_hash: str,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter
    ):
        print(f"Send GCHNK, chunk_num={chunk_num}")
        res = await download_chunk(reader, writer, chunk_hash, chunk_num)
        with open(partial_file, mode='r+b') as fp:
            fp.seek(chunk_num * CHUNK_SIZE)
            fp.write(res)

    async def connect_and_save_chunks(
            host: str,
            port: int,
            chunk_nums: list[int],
            chunk_hashes: list[str]):
        reader, writer = await asyncio.open_connection(host, port)
        for coro in [download_and_save_chunk(chunk_num, "A" * 32, reader, writer) for chunk_num, chunk_hash in
                     zip(chunk_nums, chunk_hashes)]:
            await coro

    n_chunks = math.ceil(size / CHUNK_SIZE)
    chunk_num_mapping = [
        list(range(0, n_chunks // 3)),
        list(range(n_chunks // 3, 2 * n_chunks // 3)),
        list(range(2 * n_chunks // 3, n_chunks)),
    ]

    await asyncio.gather(
        *[connect_and_save_chunks('localhost', port, chunk_nums, ['B' * 32 for _ in range(n_chunks)]) for
          port, chunk_nums in zip(range(8001, 8004), chunk_num_mapping)])

    with open(partial_file, mode='rb') as fsource:
        with open(out_name, mode='wb') as fdest:
            shutil.copyfileobj(fsource, fdest)
            fdest.seek(-(size % CHUNK_SIZE), os.SEEK_END)
            fdest.truncate()
    print(f"Wrote to {out_name}")

    os.remove(partial_file)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        download_file("c54dedc175d993f3b632a5b5bdfc9a920d2139ee8df50e8f3219ec7a462de823"[:32], 736052, 'out.jpeg'))
