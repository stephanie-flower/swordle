import dataclasses
import json

from game_model.custom_types import JsonStr
from game_model.custom_types import Char


@dataclasses.dataclass(frozen=True)
class UpdateTrueStateDTO:
    """An update to the game state (Player -> Server)"""

    player: str
    row: int
    values: list[Char]


def _as_update_true_state_dto(dct: dict) -> UpdateTrueStateDTO:
    player = dct["player_no"]
    row = dct["row"]
    values = dct["values"]
    return UpdateTrueStateDTO(player, row, values)


def parse_update_request(json_str: JsonStr) -> UpdateTrueStateDTO:
    return json.loads(json_str, object_hook=_as_update_true_state_dto)
