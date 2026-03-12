"""
Provides core functions for analysing words used in Scrabble games.
"""

from collections import Counter
import csv

from matplotlib import pyplot as plt

from GcgScraper import GcgScraper
from NgramsFinder import NgramsFinder


# CSV reader and writer settings
CSV_DELIMITER: str = " "
CSV_QUOTECHAR: str = "|"


def scrape_and_output_words_from_scrabble_games_to_text_file(text_file_path: str, max_files_to_read: int = -1, user_agent: str = None):
    """
    Scrapes GCG files from Cross-Tables.com and outputs the words in each game to a text file.
    The words are separated by newlines in the text file.
    :param text_file_path: The path to the text file where the words will be written.
    :param max_files_to_read: The maximum number of GCG files to read. If set to -1, all files will be read.
    :param user_agent: The user agent to use when scraping. If None, a default user agent will be used.
    :return: None
    """

    scraper = GcgScraper(user_agent=user_agent)
    scraper.output_words_to_file(text_file_path, max_files_to_read)


def read_scrabble_words_from_text_file_and_compute_english_and_scrabble_probabilities_to_be_stored_in_csv_file(text_file_path: str, csv_file_path: str):
    """
    Reads the words from a text file, computes the English and Scrabble probabilities for each word,
    and stores the results in a CSV file.
    The CSV file is formatted as follows:

    [WORD], [ENGLISH_PROBABILITY], [SCRABBLE_PROBABILITY]

    where
    - [WORD] is the word;
    - [ENGLISH_PROBABILITY] is the English probability of the word; and
    - [SCRABBLE_PROBABILITY] is the Scrabble probability of the word.

    :param text_file_path: The path to the text file.
    The contents of this file are assumed to be the words extracted from Scrabble games, as scraped via scrape_and_output_words_from_scrabble_games_to_text_file.
    :param csv_file_path: The path to the CSV file where the probabilities will be stored.
    :return: None
    """

    scrabble_frequency_counter = Counter()

    with open(text_file_path) as text_file:
        for line in text_file:
            word = line.removesuffix("\n")
            scrabble_frequency_counter[word] += 1

    # The number of words extracted from all Scrabble games
    # Different instances of the same word are counted separately
    num_of_scrabble_words = sum(scrabble_frequency_counter.values())

    ngrams_finder = NgramsFinder()

    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=CSV_DELIMITER, quotechar=CSV_QUOTECHAR, quoting=csv.QUOTE_MINIMAL)
        for word in scrabble_frequency_counter:
            scrabble_probability: float = scrabble_frequency_counter[word] / num_of_scrabble_words
            ngrams_probability: float = ngrams_finder.get_collapsed_relative_match_count(word)

            csv_writer.writerow([
                word,
                scrabble_probability,
                ngrams_probability
            ])


def read_csv_file_and_display_plot(csv_file_path: str, x_axis_label_for_ngrams_probabilities: str = "",
                                   y_axis_label_for_scrabble_probabilities: str = ""):
    """
    Reads the English and Scrabble probabilities of words listed in a CSV file
    and displays a plot of the two probabilities (via Matplotlib) of each word.

    The CSV file is assumed to have the format specified in
    read_scrabble_words_from_text_file_and_compute_english_and_scrabble_probabilities_to_be_stored_in_csv_file.

    :param csv_file_path: The path to the CSV file.
    :param x_axis_label_for_ngrams_probabilities: The label for the x-axis of the plot.
    :param y_axis_label_for_scrabble_probabilities: The label for the y-axis of the plot.
    :return: None
    """
    words: list[str] = []
    scrabble_probabilities: list[float] = []
    ngrams_probabilities: list[float] = []

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

    if x_axis_label_for_ngrams_probabilities:
        plt.xlabel(x_axis_label_for_ngrams_probabilities)

    if y_axis_label_for_scrabble_probabilities:
        plt.ylabel(y_axis_label_for_scrabble_probabilities)

    plt.show()
