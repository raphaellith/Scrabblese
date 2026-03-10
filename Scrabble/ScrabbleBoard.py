"""
Provides the ScrabbleBoard class which represents a Scrabble board.
"""


class ScrabbleBoard:
    """
    Represents a Scrabble board.
    As the state of the board may evolve over time throughout a game,
    each ScrabbleGame may have multiple instances of ScrabbleBoard.
    """
    def __init__(self, size):
        self.size = size
        self.__board = [["" for _ in range(self.size)] for __ in range(self.size)]

    def __str__(self) -> str:
        return "\n".join(["".join([s if s else "_" for s in row]) for row in self.board])

    def add_word(self, str):
        pass

    def get_cell(self, col, row):
        return self.__board[row][col]

    def set_cell(self, col, row, value):
        self.__board[row][col] = value
