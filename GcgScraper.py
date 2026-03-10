"""
Provides a class for scraping GCG files from Cross-Tables.com.
"""

from typing import Optional, Any, Generator

import requests
from itertools import count, islice

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from Scrabble.ScrabbleGame import ScrabbleGame


class GcgScraper:
    # Due to pagination, each page/folder of the Cross-Tables.com site lists 100 annotated games only
    GAMES_PER_PAGE = 100

    # Host URL of Cross-Tables.com
    HOST_URL = "https://www.cross-tables.com"

    # URL for the game list page on Cross-Tables.com
    GAME_LIST_PAGE_URL = f"{HOST_URL}/annolistself.php"

    def __init__(self):
        self.request_session = requests.Session()
        self.request_session.headers.update({'User-Agent': '"CustomUserAgent/1.0"'})

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
        return f"{self.GAME_LIST_PAGE_URL}?offset={offset}"

    def get_gcg_file_page_url_with_game_id(self, game_id: int) -> str:
        # e.g. https://www.cross-tables.com/annotated/selfgcg/561/anno56130.gcg
        return f"{self.HOST_URL}/annotated/selfgcg/{game_id // self.GAMES_PER_PAGE}/anno{game_id}.gcg"

    def get_gcg_files_as_generator(self) -> Generator[Optional[str], Any, None]:
        """
        Returns a generator that yields the contents of GCG files from Cross-Tables.com.
        :return: A generator that yields the contents of GCG files from Cross-Tables.com.
        """
        num_of_files_read_so_far = 0

        for offset in count(start=1, step=self.GAMES_PER_PAGE):
            game_list_url = self.get_game_list_page_url_with_offset(offset)
            game_list_soup = self.get_soup(game_list_url)

            a_tags_with_game_urls = game_list_soup.select(".tdc > a")

            if not a_tags_with_game_urls:  # No <a> tags found, meaning we've reached the end
                return

            for a_tag_with_game_url in a_tags_with_game_urls:
                game_url = urlparse(a_tag_with_game_url.get("href"))  # e.g. "annotated.php?u=56130"
                game_id = int(game_url.query.removeprefix("u="))

                gcg_file_url = self.get_gcg_file_page_url_with_game_id(game_id)
                yield self.get_html(gcg_file_url)

                num_of_files_read_so_far += 1

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
                scrabble_board = ScrabbleGame(gcg_content)
                for word in scrabble_board.all_words():
                    output_file.write(word + '\n')
