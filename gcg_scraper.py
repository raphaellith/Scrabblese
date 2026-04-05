"""
Provides a class for scraping GCG files from Cross-Tables.com.
"""

from typing import Optional, Any, Generator

import requests
from itertools import count, islice

from bs4 import BeautifulSoup, ResultSet, Tag
from urllib.parse import urlparse

from parsing.scrabble_game import ScrabbleGame


class GcgScraper:
    """
    A scraper for GCG files from Cross-Tables.com.
    """

    # Due to pagination, each page/folder of the Cross-Tables.com site lists 100 annotated games only
    GAMES_PER_PAGE: int = 100

    # Host URL of Cross-Tables.com
    HOST_URL: str = "https://www.cross-tables.com"

    # URL for the game list page on Cross-Tables.com
    GAME_LIST_PAGE_URL: str = f"{HOST_URL}/annolistself.php"

    def __init__(self, user_agent: str = None):
        """
        Initialises a GcgScraper by setting up a session with a User-Agent header.

        :param user_agent: The User-Agent header to use for the session. If not provided, a default User-Agent will be used.
        """
        self.request_session = requests.Session()
        self.request_session.headers.update({'User-Agent': user_agent if user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    def get_html(self, url: str) -> Optional[str]:
        """
        Retrieves the HTML content of a given URL.
        :param url: The URL of which to retrieve the HTML content.
        :return: The HTML content of the given URL.
        """
        print("Scraping: " + url)

        while True:
            try:
                get_result = self.request_session.get(url)
                return get_result.text
            except requests.exceptions.RequestException:
                continue

    def get_soup(self, url: str) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object for the HTML content at the given URL.
        :param url: The URL of which to retrieve the HTML content.
        :return: A BeautifulSoup object for the HTML content at the given URL.
        """
        return BeautifulSoup(self.get_html(url), 'html.parser')

    def get_game_list_page_url_with_offset(self, offset: int) -> str:
        """
        Returns the URL for the game list page on Cross-Tables.com with the given offset.
        :param offset: The offset of the game list page to retrieve.
        :return: The URL for the game list page on Cross-Tables.com with the given offset.
        """
        return f"{self.GAME_LIST_PAGE_URL}?offset={offset}"

    def get_gcg_file_page_url_with_game_id(self, game_id: int) -> str:
        """
        Returns the URL for the GCG file page on Cross-Tables.com with the given game ID.

        Example: https://www.cross-tables.com/annotated/selfgcg/561/anno56130.gcg
        :param game_id: The ID of the game for which to retrieve the GCG file page URL.
        :return: The URL for the GCG file page on Cross-Tables.com with the given game ID.
        """
        return f"{self.HOST_URL}/annotated/selfgcg/{game_id // self.GAMES_PER_PAGE}/anno{game_id}.gcg"

    def get_listed_game_id_generator(self) -> Generator[int, Any, None]:
        """
        Returns a generator that yields Cross-Tables game IDs discovered on list pages.
        :return: A generator that yields Cross-Tables game IDs.
        """
        for offset in count(start=1, step=self.GAMES_PER_PAGE):
            game_list_url: str = self.get_game_list_page_url_with_offset(offset)
            game_list_soup: BeautifulSoup = self.get_soup(game_list_url)

            a_tags_with_game_urls: ResultSet[Tag] = game_list_soup.select(".tdc > a")

            if not a_tags_with_game_urls:  # No <a> tags found, meaning we've reached the end
                return

            for a_tag_with_game_url in a_tags_with_game_urls:
                game_url = urlparse(a_tag_with_game_url.get("href"))  # e.g. "annotated.php?u=56130"
                yield int(game_url.query.removeprefix("u="))

    def get_unlisted_game_id_generator(self) -> Generator[int, Any, None]:
        """
        Returns a generator that yields Cross-Tables game IDs that are not listed on list pages.
        This gives the set of game IDs complementary to those of get_listed_game_ids_as_generator.
        :return: A generator that yields unlisted Cross-Tables game IDs.
        """
        listed_game_ids_generator: Generator[int, Any, None] = self.get_listed_game_id_generator()

        try:
            last_listed_game_id = next(listed_game_ids_generator)
        except StopIteration:
            return

        for current_listed_game_id in listed_game_ids_generator:
            for id in range(last_listed_game_id - 1, current_listed_game_id, -1):
                yield id
            last_listed_game_id = current_listed_game_id

        for id in range(last_listed_game_id - 1, -1, -1):
            yield id


    # def get_gcg_records_as_generator(self) -> Generator[dict[str, Any], Any, None]:
    #     """
    #     Returns a generator that yields game records required for persistence.
    #     :return: A generator yielding dicts with game id, list-page marker, and gcg contents.
    #     """
    #     for game_id in self.get_game_ids_as_generator():
    #         gcg_file_url: str = self.get_gcg_file_page_url_with_game_id(game_id)
    #         yield {
    #             "cross_tables_game_id": game_id,
    #             "is_on_list_page": True,
    #             "gcg_file_contents": self.get_html(gcg_file_url)
    #         }

    def get_gcg_file_contents_by_game_id(self, game_id: int) -> Optional[str]:
        """
        Retrieves the contents of a GCG file from Cross-Tables.com for a given game ID.
        :param game_id: The ID of the game for which to retrieve the GCG file contents.
        :return: The contents of the GCG file for the given game ID.
        """
        gcg_file_url: str = self.get_gcg_file_page_url_with_game_id(game_id)
        return self.get_html(gcg_file_url)

    # def get_gcg_files_as_generator(self) -> Generator[Optional[str], Any, None]:
    #     """
    #     Returns a generator that yields the contents of GCG files from Cross-Tables.com.
    #     :return: A generator that yields the contents of GCG files from Cross-Tables.com.
    #     """
    #     for gcg_record in self.get_gcg_records_as_generator():
    #         yield gcg_record["gcg_file_contents"]

    def output_words_to_file(self, file_path: str, max_files_to_read: int = -1):
        """
        Retrieves the contents of GCG files from Cross-Tables.com and outputs the words in each game to a file.
        :param file_path: The path to the file where the words will be written.
        :param max_files_to_read: The maximum number of GCG files to read. If -1, all files will be read.
        :return:
        """
        gcg_file_generator = self.get_gcg_files_as_generator()

        if max_files_to_read >= 0:
            gcg_file_generator = islice(gcg_file_generator, max_files_to_read)

        with open(file_path, "w") as output_file:
            for gcg_content in gcg_file_generator:
                scrabble_game = ScrabbleGame(gcg_content)
                for word in scrabble_game.all_words():
                    output_file.write(word + '\n')
