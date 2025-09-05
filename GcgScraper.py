import requests
from itertools import count, islice

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from ScrabbleGame import ScrabbleGame


class GcgScraper:
    def __init__(self):
        self.request_session = requests.Session()
        self.request_session.headers.update({'User-Agent': '"CustomUserAgent/1.0"'})

    def get_html(self, url: str):
        print("Scraping: " + url)

        while True:
            try:
                get_result = self.request_session.get(url)
                return get_result.text
            except requests.exceptions.RequestException:
                continue

    def get_soup(self, url: str):
        return BeautifulSoup(self.get_html(url), 'html.parser')

    def get_gcg_files_as_generator(self):
        num_of_files_read_so_far = 0

        games_per_page = 100  # Each page/folder lists 100 annotated games only

        for offset in count(start=1, step=games_per_page):
            game_list_url = f"https://www.cross-tables.com/annolistself.php?offset={offset}"
            game_list_soup = self.get_soup(game_list_url)

            a_tags_with_game_urls = game_list_soup.select(".tdc > a")

            if not a_tags_with_game_urls:  # No <a> tags found, meaning we've reached the end
                return

            for a_tag_with_game_url in a_tags_with_game_urls:
                game_url = urlparse(a_tag_with_game_url.get("href"))  # e.g. "annotated.php?u=56130"
                game_id = int(game_url.query.removeprefix("u="))

                gcg_file_url = f"https://www.cross-tables.com/annotated/selfgcg/{game_id // games_per_page}/anno{game_id}.gcg"  # e.g. https://www.cross-tables.com/annotated/selfgcg/561/anno56130.gcg
                yield self.get_html(gcg_file_url)

                num_of_files_read_so_far += 1

    def output_words_to_file(self, file_path: str, max_files_to_read: int = -1):
        gcg_file_generator = self.get_gcg_files_as_generator()

        if max_files_to_read >= 0:
            gcg_file_generator = islice(gcg_file_generator, max_files_to_read)

        with open(file_path, "w") as output_file:
            for gcg_content in gcg_file_generator:
                scrabble_board = ScrabbleGame(gcg_content)
                for word in scrabble_board.all_words():
                    output_file.write(word + '\n')
