import dataclasses

from game_model.custom_types import Char
from game_model.json_interfaces.true_state import UpdateTrueStateDTO


@dataclasses.dataclass(frozen=True)
class Coordinate:
    row: int
    col: int


@dataclasses.dataclass(frozen=True)
class GameBoard:
    board: dict[Coordinate, Char]


@dataclasses.dataclass(frozen=True)
class GameState:
    """The true game state."""

    boards: list[GameBoard]


def update_game_state(
    prev_game_state: GameState, update_request: UpdateTrueStateDTO
) -> GameState:
    coord = Coordinate(update_request.row, update_request.col)
    old_boards = prev_game_state.boards
    board_index = update_request.player_no
    old_board = old_boards[update_request.player_no]
    new_board = GameBoard(_update_dict(old_board.board, coord, update_request.value))
    new_boards = [
        val if ind != board_index else new_board for ind, val in enumerate(old_boards)
    ]
    return dataclasses.replace(prev_game_state, boards=new_boards)


def _update_dict(dct: dict, key, value) -> dict:
    return {**dct, key: value}
