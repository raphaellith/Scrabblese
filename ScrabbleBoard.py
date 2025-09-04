"""
For GCG syntax, see https://www.poslfit.com/scrabble/gcg/.
"""

import re

def parse_coordinates(coordinates: str) -> tuple[int, int, bool]:
    """
    :param coordinates: A string in GCG syntax
    :return: A tuple containing an integer x-coordinate (0-14), an integer y-coordinate (0-14), and a boolean indicating if the word added is placed horizontally.
    """
    num_pattern = r"(?P<num>[1-9]|1[0-5])"
    letter_pattern = r"(?P<letter>[A-O])"

    match_with_num_first = re.fullmatch(num_pattern + letter_pattern, coordinates)
    is_horizontal = match_with_num_first is not None

    if is_horizontal:
        group_dict = match_with_num_first.groupdict()
    else:
        match_with_letter_first = re.fullmatch(letter_pattern + num_pattern, coordinates)
        group_dict = match_with_letter_first.groupdict()

    y = int(group_dict['num']) - 1
    x = ord(group_dict['letter']) - ord('A')

    return x, y, is_horizontal


class ScrabbleBoard:
    def __init__(self, gcg_file_content: str):
        self.size: int = 15
        self.grid: list[list[str]] = [["" for _ in range(self.size)] for __ in range(self.size)]
        self.words: list[str] = []

        self.__init_from_gcg_file(gcg_file_content)

    def __str__(self) -> str:
        return "\n".join(["".join([s if s else "_" for s in row]) for row in self.grid])

    def __init_from_gcg_file(self, gcg_file_content: str):
        player_nickname_pattern = r">.+:"
        rack_pattern = r"[A-Z\?]{,7}"
        coordinate_pattern = r"(?P<coord>[A-O0-9]{2,3})"
        word_formed_pattern = r"(?P<word>[A-Za-z\.]{2,})"
        signed_score_pattern = r"[\+-][0-9]+"
        cumulative_score_pattern = r"[0-9]+"

        regular_play_event_lines_pattern = r"\s".join([
            player_nickname_pattern,
            rack_pattern,
            coordinate_pattern,
            word_formed_pattern,
            signed_score_pattern,
            cumulative_score_pattern
        ])

        matches = re.findall(regular_play_event_lines_pattern, gcg_file_content)

        for match in matches:
            coordinates, word = match
            x, y, is_horizontal = parse_coordinates(coordinates)
            self.__add_move(x, y, is_horizontal, word)

    def __add_move(self, x: int, y: int, is_horizontal: bool, word: str):
        word = word.upper()
        positions_of_new_tiles: set[tuple[int, int]] = set()  # Set of (x, y) positions at which new tiles are placed
        x_coords_of_new_tiles: set[int] = set()


        for letter in word:
            if not (letter == "." or self.grid[y][x]):
                self.grid[y][x] = letter
                positions_of_new_tiles.add((x, y))
                x_coords_of_new_tiles.add(x)

            if is_horizontal:
                x += 1
            else:
                y += 1

        for read_horizontally in (True, False):
            self.words += self.get_new_words_in_direction(positions_of_new_tiles, read_horizontally)


    def get_new_words_in_direction(self, positions_of_new_tiles: set[tuple[int, int]], read_horizontally: bool) -> list[str]:
        # When reading horizontally in the x direction, this stores the unique y-coordinates across newly placed tiles.
        # When reading vertically in the y direction, this stores the unique x-coordinates across newly placed tiles.
        coords_of_new_tiles: set[int] = set()

        for new_tile_position in positions_of_new_tiles:
            coords_of_new_tiles.add(new_tile_position[1 if read_horizontally else 0])

        result = []

        for coord in coords_of_new_tiles:
            curr_word = ""
            curr_word_contains_new_tiles = False

            for other_coord in range(self.size):
                xy_coords = (other_coord, coord) if read_horizontally else (coord, other_coord)

                cell_contents = self.grid[xy_coords[1]][xy_coords[0]]

                if cell_contents:  # Cell contains a tile
                    curr_word += cell_contents
                    if xy_coords in positions_of_new_tiles:
                        curr_word_contains_new_tiles = True

                else:  # Cell is empty
                    if curr_word_contains_new_tiles and len(curr_word) > 1:
                        result.append(curr_word)

                    curr_word = ""
                    curr_word_contains_new_tiles = False

            # For words at the end of the row
            if curr_word_contains_new_tiles and len(curr_word) > 1:
                result.append(curr_word)

        return result
