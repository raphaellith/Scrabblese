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
        self.size = size
        self.__board: list[list[str]] = [["" for _ in range(self.size)] for __ in range(self.size)]

    def __str__(self) -> str:
        return "\n".join(["".join([s if s else "_" for s in row]) for row in self.__board])

    def get_cell(self, col, row) -> str:
        return self.__board[row][col]

    def set_cell(self, col, row, value):
        self.__board[row][col] = value

    def deep_copy(self) -> 'ScrabbleBoard':
        return deepcopy(self)
