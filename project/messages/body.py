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


GCHNK_body = namedtuple("GCHNK_body", ("msg_type", "file_hash", "chunk_num"))
SCHNK_body = namedtuple("SCHNK_body", ("msg_type", "file_hash", "chunk_num", "chunk_hash", "content"))
APEER_body = namedtuple("APEER_body", ("msg_type", "file_hash"))
PEERS_body = namedtuple("PEERS_body", ("msg_type", "chunk_num", "chunk_hashes", "file_hash", "file_size", "peers"))
REPRT_body = namedtuple("REPRT_body", ("msg_type", "file_hash", "availability"))
ERROR_body = namedtuple("ERROR_BODY", ("msg_type", "error_code"))

message_body_t = Union[GCHNK_body, SCHNK_body, APEER_body, PEERS_body, REPRT_body, ERROR_body]

