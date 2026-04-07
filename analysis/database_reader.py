from collections.abc import Callable
from typing import List

from analysis.data_point import ScrabbleseDataPoint
from database.ensure_tables_exist import initialise_database
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity
from models.scrabble_game_entity import ScrabbleGameEntity

from peewee import fn, Select
from matplotlib import pyplot as plt

# TODO: Listed/Unlisted distinction/filtering


def get_query_for_retrieving_words_and_probabilities() -> Select:
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

    query = query.group_by(ScrabbleWordEntity.text, ScrabbleWordEntity.ngrams_probability)
    query = query.order_by(ScrabbleWordEntity.text)

    return query


def get_data_points() -> List[ScrabbleseDataPoint]:
    initialise_database()

    query = get_query_for_retrieving_words_and_probabilities()

    data_points = [
        ScrabbleseDataPoint(
            word=row.text,
            ngrams_probability=row.ngrams_probability,
            scrabble_play_count=row.scrabble_play_count
        )
        for row in query
    ]

    return data_points


# TODO: Extract this method to a separate class or file
def show_plot(x_axis_label_for_ngrams_probabilities: str = "",
              y_axis_label_for_scrabble_play_counts: str = "", x_logarithmic: bool = False, y_logarithmic: bool = False,
              annotated: bool = True, data_point_filter: Callable[ScrabbleseDataPoint, bool] = None):
    """
    Displays a plot (via Matplotlib) of the ngrams and Scrabble probabilities of each word.

    :param x_axis_label_for_ngrams_probabilities: The label for the x-axis of the plot.
    :param y_axis_label_for_scrabble_play_counts: The label for the y-axis of the plot.
    :param x_logarithmic: Whether to use a logarithmic scale for the x-axis of the plot.
    :param y_logarithmic: Whether to use a logarithmic scale for the y-axis of the plot.
    :param annotated: Whether to annotate each data point with the word it represents.
    :param data_point_filter: A filter for which data points to include in the plot.
    If None, all data points are included. If not None, only data points for which the filter returns True are included.
    :return: None
    """
    data_points = get_data_points()

    if data_point_filter:
        data_points = [d for d in data_points if data_point_filter(d)]

    plt.scatter([d.ngrams_probability for d in data_points], [d.scrabble_play_count for d in data_points], marker=".")

    plt.xscale("log" if x_logarithmic else "linear")
    plt.yscale("log" if y_logarithmic else "linear")

    if annotated:
        for d in data_points:
            plt.annotate(d.word, (d.ngrams_probability, d.scrabble_play_count))

    if x_axis_label_for_ngrams_probabilities:
        plt.xlabel(x_axis_label_for_ngrams_probabilities)

    if y_axis_label_for_scrabble_play_counts:
        plt.ylabel(y_axis_label_for_scrabble_play_counts)

    plt.show()
