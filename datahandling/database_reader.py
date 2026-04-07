from typing import List

from datahandling.data_point import ScrabbleseDataPoint
from database.ensure_tables_exist import initialise_database
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity
from models.scrabble_game_entity import ScrabbleGameEntity

from peewee import fn, Select


def get_query_for_retrieving_words_and_probabilities(select_listed_games: bool = True,
                                                     select_unlisted_games: bool = True) -> Select:
    if not select_listed_games and not select_unlisted_games:
        raise ValueError("At least one of select_listed_games or select_unlisted_games must be True in order for the query to return a non-empty result.")

    query = (
        ScrabbleWordEntity
        .select(
            ScrabbleWordEntity.text,
            ScrabbleWordEntity.ngrams_probability,
            fn.SUM(ScrabbleGameWordEntity.count).alias("scrabble_play_count")
        )
        .join(ScrabbleGameWordEntity, on=(ScrabbleGameWordEntity.scrabble_word_id == ScrabbleWordEntity.id))
        .join(ScrabbleGameEntity, on=(ScrabbleGameWordEntity.scrabble_game_id == ScrabbleGameEntity.id))
    )

    if select_listed_games and not select_unlisted_games:
        query = query.where(ScrabbleGameEntity.is_on_list_page == True)
    elif select_unlisted_games and select_listed_games:
        query = query.where(ScrabbleGameEntity.is_on_list_page == False)

    query = query.group_by(ScrabbleWordEntity.text, ScrabbleWordEntity.ngrams_probability)
    query = query.order_by(ScrabbleWordEntity.text)

    return query


def get_data_points(select_listed_games: bool = True, select_unlisted_games: bool = True) -> List[ScrabbleseDataPoint]:
    initialise_database()

    query = get_query_for_retrieving_words_and_probabilities(
        select_listed_games=select_listed_games,
        select_unlisted_games=select_unlisted_games
    )

    data_points = [
        ScrabbleseDataPoint(
            word=row.text,
            ngrams_probability=row.ngrams_probability,
            scrabble_play_count=row.scrabble_play_count
        )
        for row in query
    ]

    return data_points
