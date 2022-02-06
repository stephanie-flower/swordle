from enum import Enum

class GameState(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    WAITING_FOR_PLAYERS = "WAITING_FOR_PLAYERS"
    IN_GAME = "IN_GAME"
    GAME_OVER = "GAME_OVER"