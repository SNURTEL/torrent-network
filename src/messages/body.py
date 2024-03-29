from typing import Union
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


class ErrorCode(Enum):
    NO_FILE_FOUND = 0
    INTERNAL_ERROR = 1


GCHNK_body = namedtuple("GCHNK_body", ("msg_type", "file_hash", "chunk_num"))
SCHNK_body = namedtuple("SCHNK_body", ("msg_type", "file_hash", "chunk_num", "chunk_hash", "content"))
APEER_body = namedtuple("APEER_body", ("msg_type", "file_hash",))
PEERS_body = namedtuple("PEERS_body", ("msg_type", "file_hash", "file_size", "num_peers", "peers"))
REPRT_body = namedtuple("REPRT_body", ("msg_type", "file_hash", "availability", "file_size"))
ERROR_body = namedtuple("ERROR_BODY", ("msg_type", "error_code"))
ACHNK_body = namedtuple("ACHNK_body", ("msg_type", "file_hash"))
CHNKS_body = namedtuple("CHNKS_body", ("msg_type", "file_hash", "num_chunks", "availability"))

message_body_t = Union[GCHNK_body, SCHNK_body, APEER_body, PEERS_body, REPRT_body, ERROR_body, ACHNK_body, CHNKS_body]

