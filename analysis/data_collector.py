"""
Provides core functions for analysing words used in Scrabble games.
"""

from collections import Counter
from math import inf

from peewee import IntegrityError

from gcg_scraper import GcgScraper
from NgramsFinder import NgramsFinder
from parsing.scrabble_game import ScrabbleGame
from models.base_model import initialise_database
from models.scrabble_game_entity import ScrabbleGameEntity
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity


class ScrabbleseDataCollector:
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

    def scrape_and_cache_scrabble_games(self, scrape_listed_games: bool = True, max_games_to_insert: int = inf) -> int:
        """
        Scrapes game IDs and caches only games that are not already in SQLite.
        Either scrapes Scrabble games that are listed on a list page, or those that are not.
        :param scrape_listed_games: Whether to scrape listed or unlisted games.
        :param max_games_to_insert: Maximum number of games to be added to the database.
        :return: Number of newly inserted games.
        """
        initialise_database()

        game_id_generator = self.gcg_scraper.get_listed_game_id_generator() if scrape_listed_games else self.gcg_scraper.get_unlisted_game_id_generator()

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
                is_on_list_page=scrape_listed_games,
                gcg_file_contents=gcg_contents,
            )

            self._cache_game_words_to_database(scrabble_game_entity)
            inserted_games += 1

        return inserted_games
