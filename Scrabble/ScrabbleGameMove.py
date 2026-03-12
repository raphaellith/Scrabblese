"""
Represents a move in a Scrabble game.
"""


from Scrabble.ScrabbleBoard import ScrabbleBoard


class ScrabbleGameMove:
    """
    Each ScrabbleGameMove consists of a ScrabbleBoard and a list of words newly added during the move.
    The ScrabbleBoard is the state of the board after the move.
    """
    def __init__(self, board_after_move: ScrabbleBoard, words_added: list[str]):
        """
        Initialises a ScrabbleGameMove.
        :param board_after_move: The board after the move.
        :param words_added: The list of words newly added during the move.
        """
        self.board_after_move = board_after_move
        self.words_added = words_added