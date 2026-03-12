"""
Provides the ScrabbleBoard class which represents a Scrabble board.
"""

from copy import deepcopy


class ScrabbleBoard:
    """
    Represents a Scrabble board.
    As the state of the board may evolve over time throughout a game,
    each ScrabbleGame may have multiple instances of ScrabbleBoard.
    """
    def __init__(self, size):
        """
        Initialises a ScrabbleBoard of a given size.

        The attribute self._board represents the board as a 2D list of strings. These strings are either:
        - empty (""), indicating an empty cell; or
        - a single letter, indicating a cell containing a tile.

        :param size: The width and height of the board.
        """
        self.size: int = size
        self._board: list[list[str]] = [["" for _ in range(self.size)] for __ in range(self.size)]

    def __str__(self) -> str:
        """
        Returns a string representation of the board, with each row separated by a newline character.
        Empty cells are represented by an underscore.
        :return: A string representation of the board.
        """
        return "\n".join(["".join([s if s else "_" for s in row]) for row in self._board])

    def get_cell(self, col, row) -> str:
        """
        Returns the value of the cell at the given (column, row) position.
        :param col: The column position of the cell.
        :param row: The row position of the cell.
        :return: Either an empty string (""), indicating an empty cell;
        or a single letter, indicating a cell containing a tile.
        """
        return self._board[row][col]

    def set_cell(self, col, row, value):
        """
        Sets the value of the cell at the given (column, row) position.
        :param col: The column position of the cell.
        :param row: The row position of the cell.
        :param value: The value to set.
        :return: None.
        """
        self._board[row][col] = value

    def deep_copy(self) -> 'ScrabbleBoard':
        """
        Returns a deep copy of the board.
        :return: A deep copy of the board.
        """
        return deepcopy(self)
