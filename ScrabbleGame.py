"""
For GCG syntax, see https://www.poslfit.com/scrabble/gcg/.
"""

import re
from copy import deepcopy

from Stack import Stack


PLAYER_NICKNAME_PATTERN = r">.+:"
RACK_PATTERN = r"[A-Z\?]{,7}"
COORDINATE_PATTERN = r"(?P<coord>[A-O0-9]{2,3})"
WORD_FORMED_PATTERN = r"(?P<word>[A-Za-z\.]{2,})"
SIGNED_SCORE_PATTERN = r"[\+-][0-9]+"
CUMULATIVE_SCORE_PATTERN = r"[0-9]+"

REGULAR_PLAY_EVENT_LINE_PATTERN = r"\s+".join([
    PLAYER_NICKNAME_PATTERN,
    RACK_PATTERN,
    COORDINATE_PATTERN,
    WORD_FORMED_PATTERN,
    SIGNED_SCORE_PATTERN,
    CUMULATIVE_SCORE_PATTERN
])

WITHDRAWN_WORD_EVENT_LINE_PATTERN = r"\s+".join([
    PLAYER_NICKNAME_PATTERN,
    RACK_PATTERN,
    "--",
    SIGNED_SCORE_PATTERN,
    CUMULATIVE_SCORE_PATTERN
])


class ScrabbleGame:
    def __init__(self, gcg_file_content: str):
        self.size: int = 15

        self.board_evolution: Stack = Stack()  # containing elements of type list[list[str]]
        self.board_evolution.push([["" for _ in range(self.size)] for __ in range(self.size)])

        self.words_added_in_each_move: Stack = Stack()  # containing elements of type list[str]

        self.__init_from_gcg_file(gcg_file_content)

    def __str__(self) -> str:
        return "\n".join(["".join([s if s else "_" for s in row]) for row in self.board_evolution.peek()])

    def __init_from_gcg_file(self, gcg_file_content: str):
        lines = gcg_file_content.split("\n")
        lines = [line.removesuffix("\r") for line in lines]  # Carriage return present in some gcg files

        for line in lines:
            regular_play_event_match = re.fullmatch(REGULAR_PLAY_EVENT_LINE_PATTERN, line)
            if regular_play_event_match:
                coordinates, word = regular_play_event_match.groups()
                x, y, is_horizontal = parse_coordinates(coordinates)
                self.__add_move(x, y, is_horizontal, word)

            elif re.fullmatch(WITHDRAWN_WORD_EVENT_LINE_PATTERN, line):
                self.__withdraw_previous_move()

    def __add_move(self, x: int, y: int, is_horizontal: bool, word: str):
        word = word.upper()
        positions_of_new_tiles: set[tuple[int, int]] = set()  # Set of (x, y) positions at which new tiles are placed

        current_board_copy = deepcopy(self.board_evolution.peek())

        for letter in word:
            if not (letter == "." or current_board_copy[y][x]):
                current_board_copy[y][x] = letter
                positions_of_new_tiles.add((x, y))

            if is_horizontal:
                x += 1
            else:
                y += 1

        self.board_evolution.push(current_board_copy)

        new_words = []
        for read_horizontally in (True, False):
            new_words += self.get_new_words_in_direction(positions_of_new_tiles, read_horizontally)

        self.words_added_in_each_move.push(new_words)

    def __withdraw_previous_move(self):
        self.board_evolution.pop()
        self.words_added_in_each_move.pop()

    def get_new_words_in_direction(self, positions_of_new_tiles: set[tuple[int, int]], read_horizontally: bool) -> list[str]:
        # When reading horizontally in the x direction, this stores the unique y-coordinates across newly placed tiles.
        # When reading vertically in the y direction, this stores the unique x-coordinates across newly placed tiles.
        coords_of_new_tiles: set[int] = set()
        new_board = self.board_evolution.peek()

        for new_tile_position in positions_of_new_tiles:
            coords_of_new_tiles.add(new_tile_position[1 if read_horizontally else 0])

        result = []

        for coord in coords_of_new_tiles:
            curr_word = ""
            curr_word_contains_new_tiles = False

            for other_coord in range(self.size):
                xy_coords = (other_coord, coord) if read_horizontally else (coord, other_coord)

                cell_contents = new_board[xy_coords[1]][xy_coords[0]]

                if cell_contents:  # Cell contains a tile
                    curr_word += cell_contents
                    if xy_coords in positions_of_new_tiles:
                        curr_word_contains_new_tiles = True

                else:  # Cell is empty
                    if curr_word_contains_new_tiles and len(curr_word) > 1:
                        result.append(curr_word)

                    curr_word = ""
                    curr_word_contains_new_tiles = False

            # For words at the end of the row
            if curr_word_contains_new_tiles and len(curr_word) > 1:
                result.append(curr_word)

        return result

    def all_words(self):
        return sum(self.words_added_in_each_move.as_list(), start=[])



def parse_coordinates(coordinates: str) -> tuple[int, int, bool]:
    """
    :param coordinates: A string in GCG syntax
    :return: A tuple containing an integer x-coordinate (0-14), an integer y-coordinate (0-14), and a boolean indicating if the word added is placed horizontally.
    """
    num_pattern = r"(?P<num>[1-9]|1[0-5])"
    letter_pattern = r"(?P<letter>[A-O])"

    match_with_num_first = re.fullmatch(num_pattern + letter_pattern, coordinates)
    is_horizontal = match_with_num_first is not None

    if is_horizontal:
        group_dict = match_with_num_first.groupdict()
    else:
        match_with_letter_first = re.fullmatch(letter_pattern + num_pattern, coordinates)
        group_dict = match_with_letter_first.groupdict()

    y = int(group_dict['num']) - 1
    x = ord(group_dict['letter']) - ord('A')

    return x, y, is_horizontal
