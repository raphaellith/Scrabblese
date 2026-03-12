"""
Provides a class for representing a stack of ScrabbleGameMoves.
"""

from Scrabble.ScrabbleGameMove import ScrabbleGameMove


class ScrabbleGameMoveStack:
    """
    Represents a stack of ScrabbleGameMoves. Uses a list as the underlying data structure for storing moves.
    """
    def __init__(self):
        """
        Initialises an empty stack of ScrabbleGameMoves.
        """
        self._stack: list[ScrabbleGameMove] = []

    def push(self, move: ScrabbleGameMove):
        """
        Pushes a ScrabbleGameMove onto the stack.
        :param move: The ScrabbleGameMove to be pushed onto the stack.
        :return: None.
        """
        self._stack.append(move)

    def pop(self) -> ScrabbleGameMove:
        """
        Pops and returns a ScrabbleGameMove from the stack.
        :return: The ScrabbleGameMove that was popped from the stack.
        """
        return self._stack.pop()

    def peek(self) -> ScrabbleGameMove:
        """
        Returns the topmost ScrabbleGameMove on the stack without removing it.
        :return: The topmost ScrabbleGameMove on the stack.
        """
        return self._stack[-1]

    def as_list(self) -> list[ScrabbleGameMove]:
        """
        Returns the moves in the stack as a list.
        :return: A list of ScrabbleGameMoves.
        """
        return self._stack[:]