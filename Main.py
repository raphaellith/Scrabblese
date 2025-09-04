from GcgScraper import GcgScraper
from collections import Counter


scrabble_words_file_path = "ScrabbleWords.txt"

def output_words_to_file():
    scraper = GcgScraper()
    scraper.output_words_to_file(1000, scrabble_words_file_path)


def count_words_in_file() -> Counter:
    counter = Counter()

    with open(scrabble_words_file_path) as f:
        for line in f:
            word = line.removesuffix("\n")
            counter[word] += 1

    return counter
