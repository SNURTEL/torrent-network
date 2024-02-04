import asyncio
import os
from hashlib import sha256

from src.messages.body import MsgType, REPRT_body
from src.messages.pack import pack


RESOURCE_DIR = "resources"

COORDINATOR_ADDR = '10.5.0.10'
COORDINATOR_PORT = 8000
COORDINATOR_CONN_RETRY_SECONDS = 10

file_hashes_t = dict[str, str]


async def send_file_report(previous_file_hashes: file_hashes_t) -> file_hashes_t:
    """
    Check file availability in resource dir and report all to coordinator (including deleted ones).
    Return current file -> hash mapping
    """
    filenames = get_files_in_resource_dir()
    current_file_hashes = {}
    to_send = []

    for removed in filter(lambda i: i not in filenames, previous_file_hashes.keys()):
        reprt_msg = pack(
            REPRT_body(msg_type=MsgType.REPRT.value, file_hash=str.encode(previous_file_hashes[removed]), availability=0, file_size=0)
        )
        to_send.append(reprt_msg)

    for filename in filenames:
        file_path = os.path.join(RESOURCE_DIR, filename)

        with open(file_path, mode='rb') as fp:
            content = fp.read()
            file_hash = sha256(content).hexdigest()[:32]
        current_file_hashes[filename] = file_hash
        if filename.endswith(".partial"):
            av = 1
        else:
            av = 2
        reprt_msg = pack(
            REPRT_body(msg_type=MsgType.REPRT.value, file_hash=str.encode(file_hash), availability=av, file_size=len(content))
        )
        to_send.append(reprt_msg)

    if not to_send:
        return current_file_hashes

    writer = None
    try:
        writer = None
        while not writer:
            try:
                reader, writer = await asyncio.open_connection(COORDINATOR_ADDR, COORDINATOR_PORT)
            except OSError as e:
                print(f"Coordinator not available ({repr(e)}), retrying in {COORDINATOR_CONN_RETRY_SECONDS} seconds")
        for raport in to_send:
            writer.write(raport)
            with open("server.log", mode='a') as fp:
                fp.write(f"report {raport}, length={len(raport)}")
        await writer.drain()
    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()


    return current_file_hashes


def get_resource_dir_hashes() -> file_hashes_t:
    """
    Get filename -> hash mapping for all files in resource dir
    """
    files = get_files_in_resource_dir()
    dir_state = {}
    for file in files:
        file_path = os.path.join(RESOURCE_DIR, file)
        with open(file_path, mode='rb') as f:
            content = f.read()
            hash = sha256(content).hexdigest()[:32]
        dir_state[file] = hash
    return dir_state


def get_files_in_resource_dir() -> list[str]:
    """
    Get names of all files in resource dir. Create the resource dir if it does not exist
    """
    try:
        files = [f for f in os.listdir(RESOURCE_DIR) if os.path.isfile(os.path.join(RESOURCE_DIR, f))]
    except FileNotFoundError:
        files = []
        os.mkdir(RESOURCE_DIR)
    return files


async def report_availability_periodically(reporting_interval: int):
    """
    Periodically report availability of all files in resource directory
    """
    file_state = get_resource_dir_hashes()
    while True:
        try:
            file_state = await send_file_report(file_state)
            print(f"Available files: {file_state}")
            await asyncio.sleep(reporting_interval)
        except KeyboardInterrupt:
            break
