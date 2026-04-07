from dataclasses import dataclass

@dataclass(frozen=True)
class ScrabbleseDataPoint:
    word: str
    scrabble_play_count: float
    ngrams_probability: float
