import dataclasses
import json
import re
import sys
import time
from functools import reduce
from itertools import accumulate
from itertools import groupby
import socket
from typing import Callable
from typing import Iterator
from typing import Optional
from typing import TypeVar

import pandas as pd

from game_model.custom_types import Char
from game_model.custom_types import JsonStr
from game_model.json_interfaces.true_state import parse_update_request
from game_model.json_interfaces.view_state import CharState
from game_model.json_interfaces.view_state import UpdateViewStateDTO

_ROWS = 0
T = TypeVar("T")
Predicate = Callable[[T], bool]


@dataclasses.dataclass(frozen=False)
class PlayerMove:
    guesses: list[Char]


@dataclasses.dataclass
class PlayerState:
    moves: list[PlayerMove]
    correctness: list[list[CharState]]


def make_guesses(
    sock: socket,
    player_number: int,
    max_guesses: int,
    words: pd.DataFrame,
    sleep_for: int,
):
    state = PlayerState([], [])
    attempt_number = 0
    while attempt_number < max_guesses:
        time.sleep(sleep_for)
        guess = words.word.loc[0]
        make_guess(sock, player_number, attempt_number, guess)
        results: list[CharState] = get_information_update(sock, player_number)
        filters = get_filters_from_results(guess, results)
        words = update_possible_words(words, filters)
        attempt_number += 1


def get_filters_from_results(word: str, results: list[CharState]) -> list[Predicate]:
    correct_placement_regex = ["."] * len(word)
    for i, (ch, result) in enumerate(zip(word, results)):
        if result == CharState.CORRECT_PLACEMENT:
            correct_placement_regex[i] = ch
    correct_placement_lambda: list[Predicate] = [
        lambda word: bool(re.match("".join(correct_placement_regex), word))
    ]

    correct_letter_lambdas: list[Predicate] = [
        lambda word: bool(re.match(f".*{ch}.*", word))
        for ch, validity in zip(word, results)
        if validity == CharState.CORRECT_LETTER
    ]

    incorrect_letter_regexes: list[Predicate] = [
        lambda word: ch not in word
        for ch, validity in zip(word, results)
        if validity == CharState.CORRECT_LETTER
    ]

    return correct_placement_lambda + correct_letter_lambdas + incorrect_letter_regexes


def get_information_update(sock: socket, player_number: int) -> list[CharState]:
    while True:
        view_update: UpdateViewStateDTO = read_from_socket(sock)
        if view_update.player == player_number:
            return view_update.results
        elif view_update.player != player_number and all(
            [res == CharState.CORRECT_PLACEMENT for res in view_update.results]
        ):
            sys.exit("You loose")


def read_from_socket(sock: socket) -> UpdateViewStateDTO:
    msg = ""
    open_close_count = 0
    while len(msg) != 0 and open_close_count == 0:
        ch = str(sock.recv(1), "UTF-8")
        if ch == "{":
            open_close_count += 1
        elif ch == "}":
            open_close_count += -1
        msg = msg + ch
    return parse_view_update(msg)


def parse_view_update(json_str: JsonStr) -> UpdateViewStateDTO:
    return json.loads(json_str, object_hook=_as_view_update)


def _as_view_update(dct: dict) -> UpdateViewStateDTO:
    return UpdateViewStateDTO(dct["player"], dct["row"], dct["results"])


def make_guess(
    sock: socket, player_number: int, attempt_number: int, word: str
) -> None:
    msg = guess_to_json(player_number, attempt_number, word)
    sock.send(bytes(msg, "UTF-8"))


def guess_to_json(player_number: int, attempt_number: int, word: str) -> str:
    return f"""
{{
    player_no: {player_number},
    row: {attempt_number},
    value: {list(word)}
}}
"""


def update_moves(player_state: PlayerState, move: PlayerMove) -> PlayerState:
    new_moves = player_state.moves + [move]
    return dataclasses.replace(player_state, moves=new_moves)


def _filter_df(
    df: pd.DataFrame, column: pd.Series, condition: Predicate
) -> pd.DataFrame:
    return df[column.apply(condition)]


def update_possible_words(
    curr_words: pd.DataFrame, conditions: list[Predicate]
) -> pd.DataFrame:
    return reduce(
        lambda df, cond: _filter_df(df, df.word, cond), conditions, curr_words
    )


def open_web_socket(port: str) -> socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", port, "/ws/session/0/"))
    return sock


def main() -> None:
    args = sys.argv[1:]
    port = args[0]
    word_file = args[1]
    max_guesses = int(args[2])
    sleep_time = int(args[3])
    player_num = int(args[4])
    with open_web_socket(port) as sock:
        words = pd.read_csv(word_file, names=["word"])
        make_guesses(sock, player_num, max_guesses, words, sleep_time)
