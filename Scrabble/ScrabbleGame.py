"""
Provides the ScrabbleGame class which represents a Scrabble game.
"""

import re

from Scrabble.CoordinatesParsing import parse_gcg_coordinates
from Scrabble.ScrabbleBoard import ScrabbleBoard
from Scrabble.ScrabbleGameMove import ScrabbleGameMove
from Scrabble.ScrabbleGameMoveStack import ScrabbleGameMoveStack

from Scrabble.GcgRegexPatterns import REGULAR_PLAY_EVENT_LINE_PATTERN, WITHDRAWN_WORD_EVENT_LINE_PATTERN


class ScrabbleGame:
    """
    A ScrabbleGame consists of a stack of ScrabbleGameMoves and can be initialised from the contents of a GCG file.
    """

    BOARD_SIZE: int = 15

    def __init__(self, gcg_file_content: str):
        """
        Initialises a ScrabbleGame from a GCG file.

        :param gcg_file_content: The contents of a GCG file.
        """

        self.moves: ScrabbleGameMoveStack = ScrabbleGameMoveStack()
        self.moves.push(ScrabbleGameMove(board_after_move=ScrabbleBoard(self.BOARD_SIZE), words_added=[]))

        self.__init_from_gcg_file(gcg_file_content)

    def __str__(self) -> str:
        """
        :return: The string representation of the most recent board.
        """
        return str(self.moves.peek().board_after_move)

    def __init_from_gcg_file(self, gcg_file_content: str):
        """
        Initialises self.moves by simulating a game based on the contents of a GCG file.
        :param gcg_file_content: The contents of a GCG file.
        :return: None
        """

        lines = gcg_file_content.split("\n")

        # Carriage return is present in some gcg files
        lines = map(lambda l: l.removesuffix("\r"), lines)

        for line in lines:
            regular_play_event_line_pattern_match = re.fullmatch(REGULAR_PLAY_EVENT_LINE_PATTERN, line)

            # Determine whether the line refers to a regular play event or a withdrawal
            if regular_play_event_line_pattern_match:
                gcg_coordinates, word = regular_play_event_line_pattern_match.groups()
                col, row, is_horizontal = parse_gcg_coordinates(gcg_coordinates)
                self.__add_move(col, row, is_horizontal, word)

            elif re.fullmatch(WITHDRAWN_WORD_EVENT_LINE_PATTERN, line):
                self.__withdraw_previous_move()

    def __add_move(self, col: int, row: int, is_horizontal: bool, word: str):
        """
        Simulates a move by adding a word to the board and updating the stack of moves.
        :param col: The column position at which the word is placed.
        :param row: The row position at which the word is placed.
        :param is_horizontal: True if the word is placed horizontally, False if the word is placed vertically.
        :param word: The word to be added to the board.
        :return: None
        """

        word = word.upper()

        # Set of (col, row) positions at which new tiles are placed
        new_tile_positions: set[tuple[int, int]] = set()

        # Create a copy of the current board and update it with this move
        board_after_move: ScrabbleBoard = self.moves.peek().board_after_move.deep_copy()

        # Add new word to the board
        for letter in word:
            if not (letter == "." or board_after_move.get_cell(col, row)):
                board_after_move.set_cell(col, row, letter)
                new_tile_positions.add((col, row))

            if is_horizontal:
                col += 1
            else:
                row += 1

        # Record newly created words
        new_words = []
        for read_horizontally in (True, False):
            new_words += self.__get_new_words_in_direction(board_after_move, new_tile_positions, read_horizontally)

        # Update stack of moves
        self.moves.push(ScrabbleGameMove(board_after_move, new_words))

    def __withdraw_previous_move(self):
        """
        Withdraws the most recent move from the stack of moves.
        :return: None
        """
        self.moves.pop()

    def __get_new_words_in_direction(self, board_after_move: ScrabbleBoard, new_tile_positions: set[tuple[int, int]], read_horizontally: bool) -> list[str]:
        """
        Given a reading direction (horizontal or vertical), returns a list of words newly created by a move.
        :param board_after_move: The board after the move.
        :param new_tile_positions: The set of (col, row) positions at which new tiles are placed during the move.
        :param read_horizontally: To retrieve new words horizontally, set to True.
        To retrieve new words vertically, set to False.
        :return: The list of words newly created by a move in the specified direction.
        """

        # When reading horizontally, this stores the unique column-coordinates across newly placed tiles.
        # When reading vertically, this stores the unique row-coordinates across newly placed tiles.
        row_or_column_indices_with_new_tiles: set[int] = set()

        for new_tile_position in new_tile_positions:
            row_or_column_indices_with_new_tiles.add(new_tile_position[0 if read_horizontally else 1])

        result: list[str] = []

        for row_or_column_index in row_or_column_indices_with_new_tiles:
            curr_word = ""
            curr_word_contains_new_tiles = False

            for other_coord in range(self.BOARD_SIZE):
                coordinates: tuple[int, int] = (row_or_column_index, other_coord) if read_horizontally else (other_coord, row_or_column_index)

                cell_contents = board_after_move.get_cell(*coordinates)

                if cell_contents:  # Cell contains a tile
                    curr_word += cell_contents
                    if coordinates in new_tile_positions:
                        curr_word_contains_new_tiles = True

                else:  # Cell is empty
                    if curr_word_contains_new_tiles and len(curr_word) > 1:
                        result.append(curr_word)

                    curr_word = ""
                    curr_word_contains_new_tiles = False

            # For words at the end of the row/column
            if curr_word_contains_new_tiles and len(curr_word) > 1:
                result.append(curr_word)

        return result

    def all_words(self) -> list[str]:
        """
        Returns a list of all words added during the game.
        :return: A list of all words added during the game.
        """
        return sum([move.words_added for move in self.moves.as_list()], start=[])

