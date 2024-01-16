import struct
from typing import NamedTuple, Any, Union
from collections import namedtuple
from enum import Enum


class MsgType(Enum):
    ERROR = 0
    APEER = 1
    PEERS = 2
    REPRT = 3
    ACHNK = 4
    CHNKS = 5
    GCHNK = 6
    SCHNK = 7


GCHNK_body = namedtuple("GCHNK_body", ("msg_type", "file_hash", "chunk_num"))
SCHNK_body = namedtuple("SCHNK_body", ("msg_type", "file_hash", "chunk_num", "chunk_hash", "content"))

message_body_t = Union[GCHNK_body, SCHNK_body]


def _pack_string(body_or_data: Union[message_body_t, bytes], msg_type: MsgType = None) -> str:
    if not ((isinstance(body_or_data, message_body_t) and msg_type is None) or (
            isinstance(body_or_data, bytes) and msg_type is not None)):
        raise ValueError("Provide either message_body_t with no msg_type arg or raw bytes with msg_type")

    _const_size_pack_string = {
        MsgType.GCHNK: "<Bxxx32sHxx"
    }
    _variable_size_pack_string_prefix = {
        MsgType.SCHNK: "<Bxxx32sHxx32s"
    }
    _variable_size_pack_size_without_suffix = {
        MsgType.SCHNK: 72
    }

    if isinstance(body_or_data, message_body_t):
        # deduce from message namedtuple type
        body: message_body_t = body_or_data
        if isinstance(body, (GCHNK_body,)):
            # constant size messages
            return _const_size_pack_string[MsgType(body.msg_type)]
        else:
            # variable size messages
            match body:
                case SCHNK_body():
                    return _variable_size_pack_string_prefix[MsgType(body.msg_type)] + f"{len(body.content)}s"
                case _:
                    raise NotImplementedError()
    else:
        # deduce from explicitly given message type enum val and bytes length
        data = body_or_data
        if msg_type in (MsgType.GCHNK,):
            # constant size messages
            return _const_size_pack_string[msg_type]
        else:
            # variable size messages
            print(len(data))
            return _variable_size_pack_string_prefix[
                msg_type] + f"{len(data) - _variable_size_pack_size_without_suffix[msg_type]}s"


def pack(body: message_body_t) -> bytes:
    return struct.pack(_pack_string(body), *body)


def unpack(data: bytes, msg_type: MsgType) -> message_body_t:
    print(_pack_string(data, msg_type=msg_type))
    unpacked = struct.unpack(_pack_string(data, msg_type=msg_type), data)

    # assume first field is always message type
    assert unpacked[0] == msg_type.value

    match msg_type:
        case MsgType.GCHNK:
            return GCHNK_body._make(unpacked)

        case MsgType.SCHNK:
            return SCHNK_body._make(unpacked)

        case _:
            raise NotImplementedError("Invalid message type or not implemented")


if __name__ == '__main__':
    print("Constant size example:")
    body = GCHNK_body(msg_type=MsgType.GCHNK.value, file_hash=str.encode("A" * 32), chunk_num=123)
    print(f"Body:\t\t{body}")
    packed = pack(body)
    print(f"Packed:\t\t{packed}")
    unpacked = unpack(packed, msg_type=MsgType.GCHNK)
    print(f"Unpacked:\t{unpacked}")


    print("\n\nVariable size example:")
    body = SCHNK_body(
        msg_type=MsgType.SCHNK.value,
        file_hash=str.encode("A" * 32),
        chunk_num=123,
        chunk_hash=str.encode("B" * 32),
        content=str.encode("Chunk data goes here"))
    print(f"Body:\t\t{body}")
    packed = pack(body)
    print(f"Packed:\t\t{packed}")
    unpacked = unpack(packed, msg_type=MsgType.SCHNK)
    print(f"Unpacked:\t{unpacked}")
