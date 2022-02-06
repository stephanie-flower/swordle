from enum import Enum

class MessageType(str, Enum):
    CONNECTION_OPENED = "CONNECTION_OPENED"
    SUBMIT_WORD = "SUBMIT_WORD"
    PLAYER_WIN = "PLAYER_WIN"
