from database.ensure_tables_exist import initialise_database
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity

from peewee import fn
from matplotlib import pyplot as plt


def get_words_and_probabilities():
    initialise_database()

    total_number_of_scrabble_plays = get_total_number_of_scrabble_plays()

    if total_number_of_scrabble_plays == 0:
        return [], [], []

    # Query all unique words, their ngram probabilities, and their Scrabble probabilities
    query = (
        ScrabbleWordEntity
        .select(
            ScrabbleWordEntity.text,
            ScrabbleWordEntity.ngrams_probability,
            (fn.SUM(ScrabbleGameWordEntity.count) / float(total_number_of_scrabble_plays)).alias("scrabble_probability")
        )
        .join(ScrabbleGameWordEntity, on=(ScrabbleGameWordEntity.scrabble_word_id == ScrabbleWordEntity.id))
        .group_by(ScrabbleWordEntity.text, ScrabbleWordEntity.ngrams_probability)
        .order_by(ScrabbleWordEntity.text)
    )

    words = []
    ngrams_probabilities = []
    scrabble_probabilities = []

    for row in query:
        words.append(row.text)
        ngrams_probabilities.append(row.ngrams_probability)
        scrabble_probabilities.append(row.scrabble_probability)

    return words, ngrams_probabilities, scrabble_probabilities


# def get_all_words_in_database():
#     initialise_database()
#     return ScrabbleWordEntity.select(ScrabbleWordEntity.text).order_by(ScrabbleWordEntity.text)


def get_total_number_of_scrabble_plays():
    initialise_database()
    return (ScrabbleGameWordEntity
            .select(fn.SUM(ScrabbleGameWordEntity.count))
            .scalar() or 0
            )


def show_plot(words: list[str], ngrams_probabilities: list[float],
              scrabble_probabilities: list[float], x_axis_label_for_ngrams_probabilities: str = "",
              y_axis_label_for_scrabble_probabilities: str = "", logarithmic: bool = False,
              annotated: bool = True):
    """
    Displays a plot (via Matplotlib) of the ngrams and Scrabble probabilities of each word.

    :param words: A list of words.
    :param ngrams_probabilities: The ngrams probabilities of the listed words.
    :param scrabble_probabilities: The scrabble probabilities of the listed words.
    :param x_axis_label_for_ngrams_probabilities: The label for the x-axis of the plot.
    :param y_axis_label_for_scrabble_probabilities: The label for the y-axis of the plot.
    :param logarithmic: Whether to use a logarithmic scale for the axes of the plot.
    :param annotated: Whether to annotate each data point with the word it represents.
    :return: None
    """
    plt.scatter(ngrams_probabilities, scrabble_probabilities, marker=".")

    scale_option = "log" if logarithmic else "linear"
    plt.xscale(scale_option)
    plt.yscale(scale_option)

    if annotated:
        for i, word in enumerate(words):
            plt.annotate(word, (ngrams_probabilities[i], scrabble_probabilities[i]))

    if x_axis_label_for_ngrams_probabilities:
        plt.xlabel(x_axis_label_for_ngrams_probabilities)

    if y_axis_label_for_scrabble_probabilities:
        plt.ylabel(y_axis_label_for_scrabble_probabilities)

    plt.show()


if __name__ == '__main__':
    words, ngrams_probabilities, scrabble_probabilities = get_words_and_probabilities()
    show_plot(words, ngrams_probabilities, scrabble_probabilities, logarithmic=True)
