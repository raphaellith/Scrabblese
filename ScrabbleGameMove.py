from ScrabbleBoard import ScrabbleBoard


class ScrabbleGameMove:
    def __init__(self, board_after_move: ScrabbleBoard, words_added: list[str]):
        self.board_after_move = board_after_move
        self.words_added = words_added