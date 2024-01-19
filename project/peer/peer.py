import socket
import asyncio
import math
import shutil
import os
import threading
import time
from hashlib import sha256
from peer_server import run_server

from project.messages.body import MsgType, GCHNK_body, REPRT_body, APEER_body
from project.messages.pack import pack, unpack

socket.socketpair()

CHUNK_SIZE = 1024
RESCOURSE_FOLDER = "rescources"


async def download_chunk(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, file_hash: str, chunk_num: int
) -> bytes:
    file_hash_bytes = str.encode(file_hash)
    gchnk_bytes = pack(GCHNK_body(msg_type=MsgType.GCHNK.value, file_hash=file_hash_bytes, chunk_num=chunk_num))
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
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter, file_hash: str, chunk_nums: list[int]
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
    reader, writer = await asyncio.open_connection("localhost", 8000)

    n_chunks = math.ceil(size / CHUNK_SIZE)

    partial_file = f"{out_name}.partial"

    async def download_and_save_chunk(chunk_num: int, chunk_hash: str):
        print(f"Send GCHNK, chunk_num={chunk_num}")
        res = await download_chunk(reader, writer, chunk_hash, chunk_num)
        with open(partial_file, mode="ab") as fp:
            fp.seek(chunk_num * CHUNK_SIZE)
            fp.write(res)

    for coro in [download_and_save_chunk(i, "A" * 32) for i in range(n_chunks)]:
        await coro

    with open(partial_file, mode="rb") as fsource:
        with open(out_name, mode="wb") as fdest:
            shutil.copyfileobj(fsource, fdest)
            fdest.seek(-(size % CHUNK_SIZE), os.SEEK_END)
            fdest.truncate()
    print(f"Wrote to {out_name}")

    os.remove(partial_file)


async def send_file_report(file_state):
    files = get_files()
    new_file_state = {}
    to_send = []

    for removed in filter(lambda i: i not in files, file_state.keys()):
        raport_msg = pack(
            REPRT_body(msg_type=MsgType.REPRT.value, file_hash=file_state[removed], availability=0, file_size=0)
        )
        to_send.append(raport_msg)

    for file in files:
        file_path = os.path.join(RESCOURSE_FOLDER, file)
        with open(file_path, mode="rb") as f:
            content = f.read()
            hash = str.encode(sha256(content).hexdigest())[:32]
        new_file_state[file] = hash
        if file.endswith(".partial"):
            av = 1
        else:
            av = 2
        raport_msg = pack(
            REPRT_body(msg_type=MsgType.REPRT.value, file_hash=hash, availability=av, file_size=len(content))
        )
        to_send.append(raport_msg)

    writer = None
    try:
        writer = None
        reader, writer = await asyncio.open_connection("localhost", 8000)
        for raport in to_send:
            writer.write(raport)
        await writer.drain()
    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()

    return new_file_state


async def ask_for_peers(hash):
    writer = None
    data = None
    try:
        reader, writer = await asyncio.open_connection("localhost", 8000)
        ask_for_peers_msg = pack(
            APEER_body(
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
    files = get_files()
    file_state = {}
    for file in files:
        file_path = os.path.join(RESCOURSE_FOLDER, file)
        with open(file_path, mode="rb") as f:
            content = f.read()
            hash = str.encode(sha256(content).hexdigest())[:32]
        file_state[file] = hash
    return file_state


def get_files():
    try:
        files = [f for f in os.listdir(RESCOURSE_FOLDER) if os.path.isfile(os.path.join(RESCOURSE_FOLDER, f))]
    except FileNotFoundError:
        files = []
        os.mkdir(RESCOURSE_FOLDER)
    return files


async def automatic_reporting():
    file_state = get_init_file_state()
    while True:
        try:
            file_state = await send_file_report(file_state)
            await asyncio.sleep(15)
        except KeyboardInterrupt:
            break


def run_in_new_loop(loop, coro):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()


def main():
    report_loop = asyncio.new_event_loop()
    report_thread = threading.Thread(target=run_in_new_loop, args=(report_loop, automatic_reporting()))
    report_thread.start()

    # server_loop = asyncio.new_event_loop()
    # server_thread = threading.Thread(target=run_in_new_loop, args=(server_loop, run_server()))
    # server_thread.start()

    try:
        while True:
            user_input = input("?: ")
            print(f">: {user_input}")
            main_menu(user_input=user_input)

    except KeyboardInterrupt:
        pass

    if report_thread.is_alive():
        report_thread.join()

    # if server_thread.is_alive():
    #     server_thread.join()


def main_menu(user_input):
    try:
        command, params = user_input.split(" ", 1)
    except ValueError:
        command = user_input
        params = None
    match command:
        case "download":
            if params is None:
                print("No file name provided")
                main_menu("help download")
            else:
                print(f"Downloading file{params}")
                asyncio.run(download_file(params[0][:32], 736052, params[1] if params[1] else "out.jpeg"))
        case "help":
            help(params)
        case "exit":
            print("Exiting...")
            exit()
        case _:
            print("Unknown command")


def help(params=None):
    if params is not None:
        print("Help for command:", params)
        match params:
            case "download":
                print("download <file_name> - download file <file_name> ")
            case "list":
                print("list <file_name> - list files containing <file_name>")
            case "help":
                print("help <command> - get help for command")
            case "exit":
                print("exit - exit program")
            case _:
                print("Unknown command")
    else:
        print("List of commands:")
        print("download")
        print("list")
        print("help")
        print("exit")


if __name__ == "__main__":
    print("Starting peer...")
    main()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(
    #     download_file("c54dedc175d993f3b632a5b5bdfc9a920d2139ee8df50e8f3219ec7a462de823"[:32], 736052, "out.jpeg")
    # )
