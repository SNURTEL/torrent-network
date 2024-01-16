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

GCHNK_body = namedtuple("GCHNK_body", ("msg_type", "file_hash", "chunk_num"))
SCHNK_body = namedtuple("SCHNK_body", ("msg_type", "file_hash", "chunk_num", "chunk_hash", "content"))

message_body_t = Union[GCHNK_body, SCHNK_body]

