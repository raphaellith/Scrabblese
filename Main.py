from collections import Counter
import csv

from matplotlib import pyplot as plt

from GcgScraper import GcgScraper
from NgramsFinder import NgramsFinder


# CSV reader and writer settings
CSV_DELIMITER = " "
CSV_QUOTECHAR = "|"


def scrape_and_output_words_from_scrabble_games_to_text_file(text_file_path: str, max_files_to_read: int = -1):
    scraper = GcgScraper()
    scraper.output_words_to_file(text_file_path, max_files_to_read)


def read_scrabble_words_from_text_file_and_compute_english_and_scrabble_probabilities_to_be_stored_in_csv_file(text_file_path: str, csv_file_path: str):
    scrabble_frequency_counter = Counter()

    with open(text_file_path) as text_file:
        for line in text_file:
            word = line.removesuffix("\n")
            scrabble_frequency_counter[word] += 1

    scrabble_frequency_total = sum(scrabble_frequency_counter.values())

    ngrams_finder = NgramsFinder()

    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
        for word in scrabble_frequency_counter:
            scrabble_probability = scrabble_frequency_counter[word] / scrabble_frequency_total
            ngrams_probability = ngrams_finder.get_collapsed_relative_match_count(word)
            csv_writer.writerow([
                word,
                scrabble_probability,
                ngrams_probability
            ])


def read_csv_file_and_display_plot(csv_file_path: str):
    words = []
    scrabble_probabilities = []
    ngrams_probabilities = []

    with open(csv_file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR)
        for row in csv_reader:
            word, scrabble_probability, ngram_probability = row

            scrabble_probability = float(scrabble_probability)
            ngram_probability = float(ngram_probability)

            words.append(word)
            scrabble_probabilities.append(scrabble_probability)
            ngrams_probabilities.append(ngram_probability)

    plt.scatter(ngrams_probabilities, scrabble_probabilities, marker=".")

    for i, word in enumerate(words):
        plt.annotate(word, (ngrams_probabilities[i], scrabble_probabilities[i]))

    plt.show()


if __name__ == '__main__':
    SCRABBLE_WORDS_TEXT_FILE_PATH = "Files/words.txt"
    PROBABILITIES_CSV_FILE_PATH = "Files/probabilities.csv"

    # 1
    # scrape_and_output_words_from_scrabble_games_to_text_file(SCRABBLE_WORDS_TEXT_FILE_PATH)

    # 2
    # read_text_file_and_compute_english_and_scrabble_probabilities_to_be_stored_in_csv_file(SCRABBLE_WORDS_TEXT_FILE_PATH, PROBABILITIES_CSV_FILE_PATH)

    # 3
    read_csv_file_and_display_plot(PROBABILITIES_CSV_FILE_PATH)
