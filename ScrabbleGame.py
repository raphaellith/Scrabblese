"""
Represents a Scrabble game.

A ScrabbleGame consists of a stack of ScrabbleGameMoves.
"""

import re
from copy import deepcopy

from CoordinatesParsing import parse_coordinates
from ScrabbleBoard import ScrabbleBoard
from ScrabbleGameMove import ScrabbleGameMove
from Stack import Stack

from GcgRegexPatterns import REGULAR_PLAY_EVENT_LINE_PATTERN, WITHDRAWN_WORD_EVENT_LINE_PATTERN

BOARD_SIZE = 15


class ScrabbleGame:
    def __init__(self, gcg_file_content: str):
        self.moves: Stack = Stack()
        self.moves.push(ScrabbleGameMove(board_after_move=ScrabbleBoard(BOARD_SIZE), words_added=[]))

        self.__init_from_gcg_file(gcg_file_content)

    def __str__(self) -> str:
        return str(self.moves.peek().board_after_move)

    def __init_from_gcg_file(self, gcg_file_content: str):
        lines = gcg_file_content.split("\n")

        # Carriage return is present in some gcg files
        lines = map(lambda line: line.removesuffix("\r"), lines)

        for line in lines:
            regular_play_event_match = re.fullmatch(REGULAR_PLAY_EVENT_LINE_PATTERN, line)

            # Determine whether the line refers to a regular play event or a withdrawal
            if regular_play_event_match:
                coordinates, word = regular_play_event_match.groups()
                col, row, is_horizontal = parse_coordinates(coordinates)
                self.__add_move(col, row, is_horizontal, word)

            elif re.fullmatch(WITHDRAWN_WORD_EVENT_LINE_PATTERN, line):
                self.__withdraw_previous_move()

    def __add_move(self, col: int, row: int, is_horizontal: bool, word: str):
        word = word.upper()
        positions_of_new_tiles: set[tuple[int, int]] = set()  # Set of (col, row) positions at which new tiles are placed

        current_board_copy: ScrabbleBoard = deepcopy(self.moves.peek().board_after_move)

        # Add new word to the board
        for letter in word:
            if not (letter == "." or current_board_copy.get_cell(col, row)):
                current_board_copy.set_cell(col, row, letter)
                positions_of_new_tiles.add((col, row))

            if is_horizontal:
                col += 1
            else:
                row += 1

        # Record newly created words
        new_words = []
        for read_horizontally in (True, False):
            new_words += self.__get_new_words_in_direction(positions_of_new_tiles, read_horizontally)

        self.moves.push(ScrabbleGameMove(current_board_copy, new_words))

    def __withdraw_previous_move(self):
        self.moves.pop()

    def __get_new_words_in_direction(self, new_tile_positions: set[tuple[int, int]], read_horizontally: bool) -> list[str]:
        # When reading horizontally, this stores the unique column-coordinates across newly placed tiles.
        # When reading vertically, this stores the unique row-coordinates across newly placed tiles.
        row_or_column_indices_with_new_tiles: set[int] = set()

        for new_tile_position in new_tile_positions:
            row_or_column_indices_with_new_tiles.add(new_tile_position[1 if read_horizontally else 0])

        new_board: ScrabbleBoard = self.moves.peek().board_after_move

        result = []

        for row_or_column_index in row_or_column_indices_with_new_tiles:
            curr_word = ""
            curr_word_contains_new_tiles = False

            for other_coord in range(BOARD_SIZE):
                coordinates = (row_or_column_index, other_coord) if read_horizontally else (other_coord, row_or_column_index)

                cell_contents = new_board.get_cell(*coordinates)

                if cell_contents:  # Cell contains a tile
                    curr_word += cell_contents
                    if coordinates in new_tile_positions:
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
        return sum([move.words_added for move in self.moves.as_list()], start=[])

