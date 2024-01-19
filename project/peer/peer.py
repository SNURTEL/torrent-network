import socket
import asyncio
import math
import shutil
import os
import threading
import time
from hashlib import sha256

from project.messages.body import MsgType, GCHNK_body, REPRT_body, APEER_body
from project.messages.pack import pack, unpack

socket.socketpair()

CHUNK_SIZE = 1024
RESCOURSE_FOLDER = "/home/alzer/Studia/PSI/psi/project/rescources"

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
    reader, writer = await asyncio.open_connection('localhost', 8888)

    n_chunks = math.ceil(size / CHUNK_SIZE)

    partial_file = f"{out_name}.partial"

    async def download_and_save_chunk(chunk_num: int, chunk_hash: str):
        print(f"Send GCHNK, chunk_num={chunk_num}")
        res = await download_chunk(reader, writer, chunk_hash, chunk_num)
        with open(partial_file, mode='ab') as fp:
            fp.seek(chunk_num * CHUNK_SIZE)
            fp.write(res)

    for coro in [download_and_save_chunk(i, "A" * 32) for i in range(n_chunks)]:
        await coro

    with open(partial_file, mode='rb') as fsource:
        with open(out_name, mode='wb') as fdest:
            shutil.copyfileobj(fsource, fdest)
            fdest.seek(-(size % CHUNK_SIZE), os.SEEK_END)
            fdest.truncate()
    print(f"Wrote to {out_name}")

    os.remove(partial_file)

async def send_file_raport(file_state):
    files = [f for f in os.listdir(RESCOURSE_FOLDER) if os.path.isfile(os.path.join(RESCOURSE_FOLDER, f))]
    new_file_state = {}
    to_send = []

    for removed in filter(lambda i: i not in files, file_state.keys()):
        raport_msg = pack(REPRT_body(
            msg_type=MsgType.REPRT.value,
            file_hash=file_state[removed],
            availability=0,
            file_size=0
            )
        )
        to_send.append(raport_msg)

    for file in files:
        file_path = os.path.join(RESCOURSE_FOLDER, file)
        with open(file_path, mode='rb') as f:
            content = f.read()
            hash = str.encode(sha256(content).hexdigest())[:32]
        new_file_state[file] = hash
        if file.endswith(".partial"):
            av = 1
        else:
            av = 2
        raport_msg = pack(REPRT_body(
            msg_type=MsgType.REPRT.value,
            file_hash=hash,
            availability=av,
            file_size=len(content)
            )
        )
        to_send.append(raport_msg)

    writer = None
    try:
        reader, writer = await asyncio.open_connection('localhost', 8000)
        for raport in to_send:
            writer.write(raport)
        await writer.drain()
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()
    
    return new_file_state


async def ask_for_peers(hash):
    writer = None
    data = None
    try:
        reader, writer = await asyncio.open_connection('localhost', 8000)
        ask_for_peers_msg = pack(APEER_body(
            msg_type=MsgType.APEER.value,
            file_hash=str.encode(hash),
            )
        )
        writer.write(ask_for_peers_msg)
        await writer.drain()
        data = await reader.read()
        data = unpack(data, MsgType.PEERS)
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()
    
    return data


def get_init_file_state():
    files = [f for f in os.listdir(RESCOURSE_FOLDER) if os.path.isfile(os.path.join(RESCOURSE_FOLDER, f))]
    file_state = {}
    for file in files:
        file_path = os.path.join(RESCOURSE_FOLDER, file)
        with open(file_path, mode='rb') as f:
            content = f.read()
            hash = str.encode(sha256(content).hexdigest())[:32]
        file_state[file] = hash
    return file_state
        

async def automatic_reporting():
    file_state = get_init_file_state()
    while True:
        try:
            file_state = await send_file_raport(file_state)
            await asyncio.sleep(15)
        except KeyboardInterrupt:
            break


def run_in_new_loop(loop, coro):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()


def main():
    new_loop = asyncio.new_event_loop()
    background_thread = threading.Thread(target=run_in_new_loop, args=(new_loop, automatic_reporting()))
    background_thread.start()
    try:
        while True:
            user_input = input("Enter a command: ")
            
            if user_input == "ask_for_peers":
                data = asyncio.run(ask_for_peers("c54dedc175d993f3b632a5b5bdfc9a920d2139ee8df50e8f3219ec7a462de823"[:32]))
                print(data)
    except KeyboardInterrupt:
        pass
    
    if background_thread.is_alive():
        background_thread.join()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        download_file("c54dedc175d993f3b632a5b5bdfc9a920d2139ee8df50e8f3219ec7a462de823"[:32], 736052, 'out.jpeg'))
