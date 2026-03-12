"""
Provides a helper function for parsing coordinates written in GCG syntax.
"""

import re


def parse_gcg_coordinates(coordinates: str) -> tuple[int, int, bool]:
    """
    Helper function for parsing coordinates written in GCG syntax.

    In GCG syntax, coordinates consist of a letter (A-O, for column position) and a number (1-15, for row position).
    When a word is played horizontally, the number is written first.
    When a word is played vertically, the letter is written first.

    :param coordinates: A string in GCG syntax (see above)
    :return: A tuple containing an integer column-coordinate (0-14), an integer row-coordinate (0-14), and a boolean indicating if the word added is placed horizontally.
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

    row = int(group_dict['num']) - 1
    col = ord(group_dict['letter']) - ord('A')

    return col, row, is_horizontal