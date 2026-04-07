from analysis.data_point import ScrabbleseDataPoint
from database.ensure_tables_exist import initialise_database
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity
from models.scrabble_game_entity import ScrabbleGameEntity

from peewee import fn
from matplotlib import pyplot as plt


def get_total_number_of_scrabble_plays():
    initialise_database()

    query = (
        ScrabbleGameWordEntity
        .select(fn.SUM(ScrabbleGameWordEntity.count))
        .join(ScrabbleGameEntity, on=(ScrabbleGameWordEntity.scrabble_game_id == ScrabbleGameEntity.id))
        .join(ScrabbleWordEntity, on=(ScrabbleGameWordEntity.scrabble_word_id == ScrabbleWordEntity.id))
    )

    return query.scalar() or 0


def get_query_for_retrieving_words_and_probabilities():
    total_number_of_scrabble_plays = get_total_number_of_scrabble_plays()

    if total_number_of_scrabble_plays == 0:
        raise ZeroDivisionError("No scrabble plays found, so probabilities cannot be computed.")

    query = (
        ScrabbleWordEntity
        .select(
            ScrabbleWordEntity.text,
            ScrabbleWordEntity.ngrams_probability,
            (fn.SUM(ScrabbleGameWordEntity.count) / float(total_number_of_scrabble_plays)).alias(
                "scrabble_probability")
        )
        .join(ScrabbleGameWordEntity, on=(ScrabbleGameWordEntity.scrabble_word_id == ScrabbleWordEntity.id))
        .join(ScrabbleGameEntity, on=(ScrabbleGameWordEntity.scrabble_game_id == ScrabbleGameEntity.id))
    )

    query = query.group_by(ScrabbleWordEntity.text, ScrabbleWordEntity.ngrams_probability)
    query = query.order_by(ScrabbleWordEntity.text)

    return query


def get_data_points():
    initialise_database()

    query = get_query_for_retrieving_words_and_probabilities()

    data_points = [
        ScrabbleseDataPoint(
            word=row.text,
            ngrams_probability=row.ngrams_probability,
            scrabble_probability=row.scrabble_probability
        )
        for row in query
    ]

    return data_points


# TODO: Extract this method to a separate class or file
def show_plot(x_axis_label_for_ngrams_probabilities: str = "",
              y_axis_label_for_scrabble_probabilities: str = "", logarithmic: bool = False,
              annotated: bool = True):
    """
    Displays a plot (via Matplotlib) of the ngrams and Scrabble probabilities of each word.

    :param x_axis_label_for_ngrams_probabilities: The label for the x-axis of the plot.
    :param y_axis_label_for_scrabble_probabilities: The label for the y-axis of the plot.
    :param logarithmic: Whether to use a logarithmic scale for the axes of the plot.
    :param annotated: Whether to annotate each data point with the word it represents.
    :return: None
    """
    data_points = get_data_points()
    plt.scatter([d.ngrams_probability for d in data_points], [d.scrabble_probability for d in data_points], marker=".")

    scale_option = "log" if logarithmic else "linear"
    plt.xscale(scale_option)
    plt.yscale(scale_option)

    if annotated:
        for d in data_points:
            plt.annotate(d.word, (d.ngrams_probability, d.scrabble_probability))

    if x_axis_label_for_ngrams_probabilities:
        plt.xlabel(x_axis_label_for_ngrams_probabilities)

    if y_axis_label_for_scrabble_probabilities:
        plt.ylabel(y_axis_label_for_scrabble_probabilities)

    plt.show()
