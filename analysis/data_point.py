from dataclasses import dataclass

@dataclass(frozen=True)
class ScrabbleseDataPoint:
    word: str
    scrabble_probability: float
    ngrams_probability: float
