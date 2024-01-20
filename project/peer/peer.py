import random
import socket
import asyncio
import math
import shutil
import os
from hashlib import sha256

from project.coordinator.data_classes import Peer, decode_peers
from project.messages.body import MsgType, GCHNK_body, APEER_body
from project.messages.pack import pack, unpack

socket.socketpair()

CHUNK_SIZE = 1024

async def _query_coordinator_for_file_peers(
        file_hash: str
) -> list[Peer]:
    reader, writer = await asyncio.open_connection('localhost', 8000)
    apeer_msg = pack(APEER_body(msg_type=MsgType.APEER.value, file_hash=str.encode(file_hash)))
    writer.write(apeer_msg)
    await writer.drain()
    prefix = await reader.readexactly(n=44)
    num_peers = int.from_bytes(prefix[-4:], byteorder='little', signed=False)
    peers_bytes = await reader.readexactly(n=num_peers*8)
    peers_response = unpack(prefix + peers_bytes, MsgType.PEERS)
    return decode_peers(peers_response.peers)


async def _download_chunk(
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


async def download_file(hash: str, size: int, out_name: str):
    partial_file = f"{out_name}.partial"

    with open(partial_file, "wb") as fp:
        fp.truncate(size)

    retry_queue = asyncio.Queue()

    peers = await _query_coordinator_for_file_peers(hash)
    peers = [  # override for testing purposes
        Peer(f"127.0.0.1:{port}", availability=2) for port in [8001, 8002, 8003]
    ]
    num_peers = len(peers)

    # for now assume all peers have the entire file
    num_chunks = math.ceil(size / CHUNK_SIZE)
    chunks_per_peer = math.ceil(num_chunks / num_peers)
    chunk_num_mapping = [list(range(num_chunks))[i:i + chunks_per_peer] for i in range(0, num_chunks, chunks_per_peer)]

    async def _download_and_save_chunk(
            chunk_num: int,
            chunk_hash: str,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter
    ):
        try:
            res = await _download_chunk(reader, writer, chunk_hash, chunk_num)
            if random.random() < 0.1:
                raise Exception("Random error")
            with open(partial_file, mode='r+b') as fp:
                fp.seek(chunk_num * CHUNK_SIZE)
                fp.write(res)
        except Exception as e:
            print(f"{e} on chunk {chunk_num}")
            await retry_queue.put((chunk_num, chunk_hash))

    async def connect_and_save_chunks(
            host: str,
            port: int,
            chunk_nums: list[int],
            chunk_hashes: list[str]):
        print(f"Connect to {host}:{port} and download {chunk_nums}")
        reader, writer = await asyncio.open_connection(host, port)
        for coro in [_download_and_save_chunk(chunk_num, "A" * 32, reader, writer) for chunk_num, chunk_hash in
                     zip(chunk_nums, chunk_hashes)]:
            await coro

    try:
        n_chunks = math.ceil(size / CHUNK_SIZE)

        await asyncio.gather(
            *[connect_and_save_chunks('localhost', port, chunk_nums, ['B' * 32 for _ in range(n_chunks)]) for
              port, chunk_nums in zip(range(8001, 8004), chunk_num_mapping)])

        while not retry_queue.empty():
            chunk_num, chunk_hash = await retry_queue.get()
            await asyncio.create_task(connect_and_save_chunks('localhost', random.choice([8001, 8002, 8003]), [chunk_num], [chunk_hash]))

        with open(partial_file, mode='rb') as fsource:
            with open(out_name, mode='wb') as fdest:
                shutil.copyfileobj(fsource, fdest)
                fdest.seek(-(size % CHUNK_SIZE), os.SEEK_END)
                fdest.truncate()
        print(f"Wrote to {out_name}")
    finally:
        os.remove(partial_file)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        download_file("c54dedc175d993f3b632a5b5bdfc9a920d2139ee8df50e8f3219ec7a462de823"[:32], 736052, 'out.jpeg'))
