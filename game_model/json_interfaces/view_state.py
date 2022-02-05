import dataclasses
import json
from enum import auto
from enum import Enum

from game_model.custom_types import JsonStr


class CharState(Enum):
    CORRECT_PLACEMENT = auto()
    CORRECT_LETTER = auto()
    INCORRECT = auto()


@dataclasses.dataclass(frozen=True)
class UpdateViewStateDTO:
    player: int
    row: int
    results: list[CharState]


def view_update_to_json(view_update: UpdateViewStateDTO) -> JsonStr:
    return json.dumps(
        {
            "player": view_update.player,
            "row": view_update.row,
            "results": view_update.results,
        }
    )
