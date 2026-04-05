"""
Provides core functions for analysing words used in Scrabble games.
"""

from collections import Counter
import csv
from math import inf

from matplotlib import pyplot as plt
from peewee import fn, IntegrityError

from GcgScraper import GcgScraper
from NgramsFinder import NgramsFinder
from Scrabble.ScrabbleGame import ScrabbleGame
from Scrabble.model.BaseModel import db
from Scrabble.model.ScrabbleGameEntity import ScrabbleGameEntity
from Scrabble.model.ScrabbleGameWordEntity import ScrabbleGameWordEntity
from Scrabble.model.ScrabbleWordEntity import ScrabbleWordEntity


def initialise_database():
    """
    Ensures all Scrabble cache tables exist.
    :return: None
    """
    db.connect(reuse_if_open=True)
    db.create_tables([ScrabbleGameEntity, ScrabbleWordEntity, ScrabbleGameWordEntity], safe=True)


class ScrabbleseAnalyser:
    def __init__(self, csv_delimiter: str = " ", csv_quotechar: str = "|", user_agent: str = None):
        self.csv_delimiter = csv_delimiter
        self.csv_quotechar = csv_quotechar

        self.ngrams_finder = NgramsFinder()
        self.gcg_scraper = GcgScraper(user_agent=user_agent) if user_agent is not None else GcgScraper()

    def _cache_game_words_to_database(self, scrabble_game_entity: ScrabbleGameEntity):
        """
        Given an existing ScrabbleGameEntity, parses its GCG content to extract its words and create ScrabbleWordEntity
        or ScrabbleGameWordEntity objects as needed.
        :param scrabble_game_entity: The persisted game entity.
        :return: None
        """
        game_words = ScrabbleGame(scrabble_game_entity.gcg_file_contents).all_words()
        word_counter = Counter(game_words)

        # Replace all per-game word counts to keep cache deterministic if source content changes
        ScrabbleGameWordEntity.delete().where(
            ScrabbleGameWordEntity.scrabble_game_id == scrabble_game_entity
        ).execute()

        for word_text, count in word_counter.items():
            scrabble_word_entity = self._get_or_create_scrabble_word_entity(word_text)
            ScrabbleGameWordEntity.create(
                scrabble_game_id=scrabble_game_entity,
                scrabble_word_id=scrabble_word_entity,
                count=count
            )

    def _get_or_create_scrabble_word_entity(self, word_text: str) -> ScrabbleWordEntity:
        """
        Given a word, returns the ScrabbleWordEntity with that word. If no such ScrabbleWordEntity exists, a new
        ScrabbleWordEntity containing the word and its ngrams probability is created and returned.
        :param word_text: The word represented by the ScrabbleWordEntity.
        :return: the ScrabbleWordEntity containing the inputted word and its ngrams probability.
        """
        scrabble_word_entity = ScrabbleWordEntity.get_or_none(ScrabbleWordEntity.text == word_text)

        if scrabble_word_entity is None:
            ngrams_probability = self.ngrams_finder.get_collapsed_relative_match_count(word_text)
            try:
                return ScrabbleWordEntity.create(text=word_text, ngrams_probability=ngrams_probability)
            except IntegrityError:
                # Another writer may have inserted the same unique word.
                scrabble_word_entity = ScrabbleWordEntity.get(ScrabbleWordEntity.text == word_text)

        if scrabble_word_entity.ngrams_probability is None:
            scrabble_word_entity.ngrams_probability = self.ngrams_finder.get_collapsed_relative_match_count(word_text)
            scrabble_word_entity.save(only=[ScrabbleWordEntity.ngrams_probability])

        return scrabble_word_entity

    def scrape_and_cache_scrabble_games(self, max_games_to_insert: int = inf) -> int:
        """
        Scrapes list-page game IDs and caches only games that are not already in SQLite.
        :param max_games_to_insert: Maximum number of games to be added to the database.
        :return: Number of newly inserted games.
        """
        initialise_database()

        game_id_generator = self.gcg_scraper.get_game_ids_as_generator()

        inserted_games = 0
        for game_id in game_id_generator:
            if inserted_games >= max_games_to_insert:
                break

            if ScrabbleGameEntity.select().where(ScrabbleGameEntity.cross_tables_game_id == game_id).exists():
                # Game is already cached
                continue

            gcg_contents = self.gcg_scraper.get_gcg_file_contents_by_game_id(game_id)
            scrabble_game_entity = ScrabbleGameEntity.create(
                cross_tables_game_id=game_id,
                is_on_list_page=True,
                gcg_file_contents=gcg_contents,
            )

            self._cache_game_words_to_database(scrabble_game_entity)
            inserted_games += 1

        return inserted_games

    # def write_probabilities_from_database_to_csv_file(self, csv_file_path: str):
    #     """
    #     Writes [WORD, SCRABBLE_PROBABILITY, NGRAMS_PROBABILITY] rows to CSV from cached DB data.
    #     :param csv_file_path: The target CSV path.
    #     :return: None
    #     """
    #     initialise_database()
    #
    #     total_scrabble_words = ScrabbleGameWordEntity.select(fn.SUM(ScrabbleGameWordEntity.count)).scalar() or 0
    #
    #     with open(csv_file_path, 'w', newline='') as csvfile:
    #         csv_writer = csv.writer(
    #             csvfile,
    #             delimiter=self.csv_delimiter,
    #             quotechar=self.csv_quotechar,
    #             quoting=csv.QUOTE_MINIMAL
    #         )
    #
    #         if not total_scrabble_words:
    #             return
    #
    #         frequency_rows = (
    #             ScrabbleWordEntity
    #             .select(
    #                 ScrabbleWordEntity.text,
    #                 ScrabbleWordEntity.ngrams_probability,
    #                 fn.SUM(ScrabbleGameWordEntity.count).alias("scrabble_count")
    #             )
    #             .join(ScrabbleGameWordEntity)
    #             .group_by(ScrabbleWordEntity.text, ScrabbleWordEntity.ngrams_probability)
    #             .order_by(ScrabbleWordEntity.text)
    #         )
    #
    #         for frequency_row in frequency_rows:
    #             scrabble_probability: float = frequency_row.scrabble_count / total_scrabble_words
    #             csv_writer.writerow([
    #                 frequency_row.text,
    #                 scrabble_probability,
    #                 frequency_row.ngrams_probability
    #             ])
    #
    # def scrape_and_output_words_from_scrabble_games_to_text_file(self, text_file_path: str, max_files_to_read: int = -1):
    #     """
    #     Scrapes GCG files from Cross-Tables.com and outputs the words in each game to a text file.
    #     The words are separated by newlines in the text file.
    #     :param text_file_path: The path to the text file where the words will be written.
    #     :param max_files_to_read: The maximum number of GCG files to read. If set to -1, all files will be read.
    #     :return: None
    #     """
    #     self.gcg_scraper.output_words_to_file(text_file_path, max_files_to_read)
    #
    # def read_scrabble_words_from_text_file_and_compute_english_and_scrabble_probabilities_to_be_stored_in_csv_file(self,
    #     text_file_path: str, csv_file_path: str):
    #     """
    #     Reads the words from a text file, computes the English and Scrabble probabilities for each word,
    #     and stores the results in a CSV file.
    #     The CSV file is formatted as follows:
    #
    #     [WORD], [ENGLISH_PROBABILITY], [SCRABBLE_PROBABILITY]
    #
    #     where
    #     - [WORD] is the word;
    #     - [ENGLISH_PROBABILITY] is the English probability of the word; and
    #     - [SCRABBLE_PROBABILITY] is the Scrabble probability of the word.
    #
    #     :param text_file_path: The path to the text file.
    #     The contents of this file are assumed to be the words extracted from Scrabble games, as scraped via scrape_and_output_words_from_scrabble_games_to_text_file.
    #     :param csv_file_path: The path to the CSV file where the probabilities will be stored.
    #     :return: None
    #     """
    #
    #     scrabble_frequency_counter = Counter()
    #
    #     with open(text_file_path) as text_file:
    #         for line in text_file:
    #             word = line.removesuffix("\n")
    #             scrabble_frequency_counter[word] += 1
    #
    #     # The number of words extracted from all Scrabble games
    #     # Different instances of the same word are counted separately
    #     num_of_scrabble_words = sum(scrabble_frequency_counter.values())
    #
    #     with open(csv_file_path, 'w', newline='') as csvfile:
    #         csv_writer = csv.writer(
    #             csvfile,
    #             delimiter=self.csv_delimiter,
    #             quotechar=self.csv_quotechar,
    #             quoting=csv.QUOTE_MINIMAL
    #         )
    #         for word in scrabble_frequency_counter:
    #             scrabble_probability: float = scrabble_frequency_counter[word] / num_of_scrabble_words
    #             ngrams_probability: float = self.ngrams_finder.get_collapsed_relative_match_count(word)
    #
    #             csv_writer.writerow([
    #                 word,
    #                 scrabble_probability,
    #                 ngrams_probability
    #             ])
    #
    # def read_csv_file_and_display_plot(
    #     self,
    #     csv_file_path: str,
    #     x_axis_label_for_ngrams_probabilities: str = "",
    #     y_axis_label_for_scrabble_probabilities: str = "",
    #     logarithmic: bool = False,
    #     annotated: bool = True
    # ):
    #     """
    #     Reads the English and Scrabble probabilities of words listed in a CSV file
    #     and displays a plot of the two probabilities (via Matplotlib) of each word.
    #
    #     The CSV file is assumed to have the format specified in
    #     read_scrabble_words_from_text_file_and_compute_english_and_scrabble_probabilities_to_be_stored_in_csv_file.
    #
    #     :param csv_file_path: The path to the CSV file.
    #     :param x_axis_label_for_ngrams_probabilities: The label for the x-axis of the plot.
    #     :param y_axis_label_for_scrabble_probabilities: The label for the y-axis of the plot.
    #     :return: None
    #     """
    #     words: list[str] = []
    #     scrabble_probabilities: list[float] = []
    #     ngrams_probabilities: list[float] = []
    #
    #     with open(csv_file_path, newline='') as csvfile:
    #         csv_reader = csv.reader(csvfile, delimiter=self.csv_delimiter, quotechar=self.csv_quotechar)
    #         for row in csv_reader:
    #             word, scrabble_probability, ngram_probability = row
    #
    #             scrabble_probability = float(scrabble_probability)
    #             ngram_probability = float(ngram_probability)
    #
    #             words.append(word)
    #             scrabble_probabilities.append(scrabble_probability)
    #             ngrams_probabilities.append(ngram_probability)
    #
    #     plt.scatter(ngrams_probabilities, scrabble_probabilities, marker=".")
    #
    #     scale_option = "log" if logarithmic else "linear"
    #     plt.xscale(scale_option)
    #     plt.yscale(scale_option)
    #
    #     if annotated:
    #         for i, word in enumerate(words):
    #             plt.annotate(word, (ngrams_probabilities[i], scrabble_probabilities[i]))
    #
    #     if x_axis_label_for_ngrams_probabilities:
    #         plt.xlabel(x_axis_label_for_ngrams_probabilities)
    #
    #     if y_axis_label_for_scrabble_probabilities:
    #         plt.ylabel(y_axis_label_for_scrabble_probabilities)
    #
    #     plt.show()
