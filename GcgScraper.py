import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from ScrabbleBoard import ScrabbleBoard


class GcgScraper:
    def __init__(self):
        self.request_session = requests.Session()
        self.request_session.headers.update({'User-Agent': '"CustomUserAgent/1.0"'})

    def get_html(self, url: str):
        return self.request_session.get(url).text

    def get_soup(self, url: str):
        return BeautifulSoup(self.get_html(url), 'html.parser')

    def get_gcg_files_as_generator(self, max_files_to_read: int):
        num_of_files_read_so_far = 0

        cross_tables_homepage_url = "https://www.cross-tables.com"
        num_of_games_listed_per_page = 100

        for offset in range(0, max_files_to_read, num_of_games_listed_per_page):
            # Each page lists 100 annotated games only, so we need to pass an "offset" parameter
            game_list_url = f"https://www.cross-tables.com/annolistself.php?offset={offset + 1}"
            game_list_soup = self.get_soup(game_list_url)

            a_tags_with_url_to_annotated_games = game_list_soup.select(".tdc > a")
            for a_tag_with_url_to_annotated_game in a_tags_with_url_to_annotated_games:
                if num_of_files_read_so_far >= max_files_to_read:
                    break

                annotated_game_url = urljoin(cross_tables_homepage_url, a_tag_with_url_to_annotated_game.get("href"))
                annotated_game_soup = self.get_soup(annotated_game_url)

                gcg_file_href = annotated_game_soup.find(id="bd").find_all("a")[-1].get("href")  # e.g. "./annotated/selfgcg/0/anno8.gcg"
                gcg_file_url = urljoin(cross_tables_homepage_url, gcg_file_href)
                print(annotated_game_url)
                yield self.get_html(gcg_file_url)

                num_of_files_read_so_far += 1

    def output_words_to_file(self, max_files_to_read: int, file_path: str):
        gcg_file_generator = self.get_gcg_files_as_generator(max_files_to_read)

        with open(file_path, "w") as output_file:
            for gcg_content in gcg_file_generator:
                scrabble_board = ScrabbleBoard(gcg_content)
                for word in scrabble_board.words:
                    print(word)
                    if word == "CELTIC":
                        exit()
                    output_file.write(word + '\n')
