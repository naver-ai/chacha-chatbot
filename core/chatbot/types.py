from typing import TypeAlias

import nanoid

from core.time import get_timestamp


class RegenerateRequestException(Exception):
    def __init__(self, reason: str):
        self.reason = reason


class DialogueTurn:
    def __init__(self, message: str,
                 is_user: bool = True,
                 id: str = None,
                 timestamp: int = None,
                 processing_time: int | None = None,
                 metadata: dict | None = None
                 ):
        self.message = message
        self.is_user = is_user
        self.id = id if id is not None else nanoid.generate(size=20)
        self.timestamp = timestamp if timestamp is not None else get_timestamp()
        self.processing_time = processing_time
        self.metadata = metadata


Dialogue: TypeAlias = list[DialogueTurn]
