from Scrabble.ScrabbleGameMove import ScrabbleGameMove


class ScrabbleGameMoveStack:
    def __init__(self):
        self._stack: list[ScrabbleGameMove] = []

    def push(self, move: ScrabbleGameMove):
        self._stack.append(move)

    def pop(self) -> ScrabbleGameMove:
        return self._stack.pop()

    def peek(self) -> ScrabbleGameMove:
        return self._stack[-1]

    def as_list(self) -> list[ScrabbleGameMove]:
        return self._stack[:]