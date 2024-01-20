import json
import random
import socket
import asyncio
import math
import shutil
import os
import sys
import time
from hashlib import sha256

from project.coordinator.data_classes import Peer, decode_peers
from project.messages.body import MsgType, GCHNK_body, APEER_body, ErrorCode
from project.messages.pack import pack, unpack

socket.socketpair()

CHUNK_SIZE = 1024

async def _query_coordinator_for_file_peers(
        file_hash: str
) -> list[Peer]:
    reader, writer = await asyncio.open_connection('10.5.0.10', 8000)
    apeer_msg = pack(APEER_body(msg_type=MsgType.APEER.value, file_hash=str.encode(file_hash)))
    writer.write(apeer_msg)
    await writer.drain()
    msg_type = await reader.readexactly(n=1)
    if int.from_bytes(msg_type, byteorder='little', signed=False) == MsgType.ERROR.value:
        body = await reader.readexactly(n=3)
        error_msg = unpack(msg_type+body, msg_type=MsgType.ERROR)
        if error_msg.error_code == ErrorCode.NO_FILE_FOUND.value:
            raise ValueError("File not found")
        else:
            raise ValueError("Error downloading file")
    prefix = msg_type + await reader.readexactly(n=43)
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
    assert unpacked.chunk_hash == str.encode(sha256(unpacked.content).hexdigest()[:32])

    return unpacked.content


async def download_file(fileinfo: dict, out_name: str):
    partial_file = f"{out_name}.partial"

    size = fileinfo['file_size']
    file_hash = fileinfo['file_hash']
    chunk_hashes = fileinfo['chunk_hashes']

    with open(partial_file, "wb") as fp:
        fp.truncate(size)

    retry_queue = asyncio.Queue()

    try:
        peers = await _query_coordinator_for_file_peers(file_hash)
        num_peers = len(peers)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # for now assume all peers have the entire file
    num_chunks = math.ceil(size / CHUNK_SIZE)
    chunks_per_peer = math.ceil(num_chunks / num_peers)
    chunk_num_mapping = [list(range(num_chunks))[i:i + chunks_per_peer] for i in range(0, num_chunks, chunks_per_peer)]
    chunk_hash_mapping = [chunk_hashes[i:i + chunks_per_peer] for i in range(0, num_chunks, chunks_per_peer)]

    async def _download_and_save_chunk(
            chunk_num: int,
            chunk_hash: str,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter
    ):
        try:
            res = await _download_chunk(reader, writer, chunk_hash, chunk_num)
            if sha256(res).hexdigest()[:32] != chunk_hash:
                raise ValueError(f"Chunk {chunk_num} hash not matching")
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
        for coro in [_download_and_save_chunk(chunk_num, chunk_hash, reader, writer) for chunk_num, chunk_hash in
                     zip(chunk_nums, chunk_hashes)]:
            await coro

    try:
        n_chunks = math.ceil(size / CHUNK_SIZE)
        print(n_chunks)

        await asyncio.gather(
            *[connect_and_save_chunks(peer.address, 8000, chunk_num_list, chunk_hash_list) for
              peer, chunk_num_list, chunk_hash_list in zip(peers, chunk_num_mapping, chunk_hash_mapping)])

        while not retry_queue.empty():
            chunk_num, chunk_hash = await retry_queue.get()
            await asyncio.create_task(connect_and_save_chunks(random.choice(peers).address, 8000, [chunk_num], [chunk_hash]))

        with open(partial_file, mode='rb') as fsource:
            with open(out_name, mode='wb') as fdest:
                shutil.copyfileobj(fsource, fdest)
                fdest.seek(-(CHUNK_SIZE-(size % CHUNK_SIZE)), os.SEEK_END)
                fdest.truncate()

        with open('out.jpg', mode='rb') as fp:
            out_bytes = fp.read()

        if not sha256(out_bytes).hexdigest()[:32] == file_hash:
            print(f"File hash vs expected:\n{sha256(out_bytes).hexdigest()[:32]}\n{file_hash}")
            raise ValueError(f"File hash vs expected:\n{sha256(out_bytes).hexdigest()[:32]}\n{file_hash}")

        print(f"Wrote to {out_name}")
    finally:
        os.remove(partial_file)


if __name__ == '__main__':
    time.sleep(3)
    loop = asyncio.get_event_loop()

    FILE = 'source.jpg'

    with open(f"{FILE}.fileinfo", mode='r') as fp:
        fileinfo = json.load(fp)

    loop.run_until_complete(
        download_file(fileinfo, 'out.jpg'))


    time.sleep(9999999)
