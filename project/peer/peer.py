import socket
import asyncio
import math
import shutil
import os
import threading
import time
from hashlib import sha256

from project.messages.body import MsgType, GCHNK_body, REPRT_body
from project.messages.pack import pack, unpack

socket.socketpair()

CHUNK_SIZE = 1024
RESCOURSE_FOLDER = "../rescources"

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
        response = pack(REPRT_body(
            msg_type=MsgType.REPRT.value,
            file_hash=file_state[removed],
            availability=0,
            file_size=0
            )
        )
        to_send.append(response)

    for file in files:
        file_path = os.path.join(RESCOURSE_FOLDER, file)
        with open(file_path) as f:
            content = f.read()
            hash = str.encode(sha256(content).hexdigest())
        new_file_state[file] = hash
        if file in file_state.keys() and hash == file_state[file]:
            continue
        if file.endswith(".partial"):
            av = 1
        else:
            av = 2
        response = pack(REPRT_body(
            msg_type=MsgType.REPRT.value,
            file_hash=hash,
            availability=av,
            file_size=len(content)
            )
        )
        to_send.append(response)

    try:
        reader, writer = await asyncio.open_connection('localhost', 8000)
        for raport in to_send:
            writer.write(raport)
        await writer.drain()
    finally:
        if writer and not writer.is_closing():
            writer.transport.close()
            await writer.wait_closed()
    
    return new_file_state


def get_init_file_state():
    files = [f for f in os.listdir(RESCOURSE_FOLDER) if os.path.isfile(os.path.join(RESCOURSE_FOLDER, f))]
    file_state = {}
    for file in files:
        file_path = os.path.join(RESCOURSE_FOLDER, file)
        with open(file_path) as f:
            content = f.read()
            hash = str.encode(sha256(content).hexdigest())
        file_state[file] = hash
    return file_state
        

def automatic_raporting():
    loop = asyncio.get_event_loop()
    file_state = get_init_file_state()
    while True:
        try:
            loop.run_until_complete(file_state = send_file_raport(file_state))
            time.sleep(15)
        except KeyboardInterrupt:
            break


def main():
    background_thread = threading.Thread(target=automatic_raporting)
    background_thread.start()

    try:
        while True:
            user_input = input("Enter a command: ")
            # TODO implement interface
            print(f"You entered: {user_input}")

    except KeyboardInterrupt:
        pass
    
    if background_thread.is_alive():
        background_thread.join()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        download_file("c54dedc175d993f3b632a5b5bdfc9a920d2139ee8df50e8f3219ec7a462de823"[:32], 736052, 'out.jpeg'))
