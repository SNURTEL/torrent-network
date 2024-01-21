import struct
from typing import Union, Optional

from project.messages.body import (MsgType,
                                   GCHNK_body,
                                   SCHNK_body,
                                   message_body_t,
                                   APEER_body,
                                   REPRT_body,
                                   ERROR_body,
                                   PEERS_body, ACHNK_body, CHNKS_body)


def _pack_string(body_or_data: Union[message_body_t, bytes],
                 msg_type: Optional[MsgType] = None,
                 ) -> str:
    if not ((isinstance(body_or_data, message_body_t) and msg_type is None) or (
            isinstance(body_or_data, bytes) and msg_type is not None)):
        raise ValueError("Provide either message_body_t only or raw bytes with msg_type")

    _const_size_pack_string = {
        MsgType.GCHNK: "<Bxxx32sHxx",
        MsgType.APEER: "<Bxxx32s",
        MsgType.REPRT: "<Bxxx32sBxxxI",
        MsgType.ERROR: "<BBxx",
        MsgType.ACHNK: "<Bxxx32s"
    }
    _variable_size_pack_string_prefix = {
        MsgType.SCHNK: "<Bxxx32sHxx32s",
        MsgType.PEERS: "<Bxxx32sII",
        MsgType.CHNKS: "<Bxxx32sHxx"
    }
    _variable_size_pack_size_without_suffix = {
        MsgType.SCHNK: 72,
        MsgType.PEERS: 44,
        MsgType.CHNKS: 40,
    }

    if isinstance(body_or_data, message_body_t):
        # deduce from message namedtuple type
        body: message_body_t = body_or_data
        if isinstance(body, (GCHNK_body, APEER_body, REPRT_body, ERROR_body, ACHNK_body)):
            # constant size messages
            return _const_size_pack_string[MsgType(body.msg_type)]
        else:
            # variable size messages
            match body:
                case SCHNK_body():
                    return _variable_size_pack_string_prefix[
                               MsgType(body.msg_type)] + f"{len(body.content)}s"
                case PEERS_body():
                    return _variable_size_pack_string_prefix[
                               MsgType(body.msg_type)] + f"{len(body.peers)}s"
                case CHNKS_body():
                    return _variable_size_pack_string_prefix[
                        MsgType(body.msg_type)] + f"{len(body.availability)}s"
                case _:
                    raise NotImplementedError()
    else:
        # deduce from explicitly given message type enum val and bytes length
        data = body_or_data
        if msg_type in (MsgType.GCHNK, MsgType.APEER, MsgType.REPRT, MsgType.ERROR, MsgType.ACHNK):
            # constant size messages
            return _const_size_pack_string[msg_type]
        else:
            # variable size messages
            return _variable_size_pack_string_prefix[
                       msg_type] + f"{len(data) - _variable_size_pack_size_without_suffix[msg_type]}s"


def pack(body: message_body_t) -> bytes:
    return struct.pack(_pack_string(body), *body)


def unpack(data: bytes, msg_type: MsgType) -> message_body_t:
    unpacked = struct.unpack(_pack_string(data, msg_type=msg_type), data)

    # assume first field is always message type
    assert unpacked[0] == msg_type.value

    match msg_type:
        case MsgType.GCHNK:
            return GCHNK_body._make(unpacked)

        case MsgType.SCHNK:
            return SCHNK_body._make(unpacked)

        case MsgType.APEER:
            return APEER_body._make(unpacked)

        case MsgType.REPRT:
            return REPRT_body._make(unpacked)

        case MsgType.ERROR:
            return ERROR_body._make(unpacked)
        
        case MsgType.PEERS:
            return PEERS_body._make(unpacked)

        case MsgType.PEERS:
            return PEERS_body._make(unpacked)

        case MsgType.ACHNK:
            return ACHNK_body._make(unpacked)

        case MsgType.CHNKS:
            return CHNKS_body._make(unpacked)

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
