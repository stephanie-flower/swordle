import dataclasses
import json

from game_model.custom_types import Char
from game_model.custom_types import JsonStr


@dataclasses.dataclass(frozen=True)
class UpdateTrueStateDTO:
    """An update to the game state (Player -> Server)"""

    player_no: int
    row: int
    value: list[Char]


def _as_update_true_state_dto(dct: dict) -> UpdateTrueStateDTO:
    player_no = dct["player_no"]
    row = dct["row"]
    value = dct["value"]
    return UpdateTrueStateDTO(player_no, row, value)


def parse_update_request(json_str: JsonStr) -> UpdateTrueStateDTO:
    return json.loads(json_str, object_hook=_as_update_true_state_dto)
