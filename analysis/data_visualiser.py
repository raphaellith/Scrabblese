from database.ensure_tables_exist import initialise_database
from models.scrabble_game_word_entity import ScrabbleGameWordEntity
from models.scrabble_word_entity import ScrabbleWordEntity
from models.scrabble_game_entity import ScrabbleGameEntity

from peewee import fn, Expression
from matplotlib import pyplot as plt


class ScrabbleseDataVisualiser:
    def __init__(self):
        self._where_expressions: list[Expression] = []

    def add_where_expression(self, where_expression: Expression):
        self._where_expressions.append(where_expression)

    def get_query_for_retrieving_words_and_probabilities(self):
        total_number_of_scrabble_plays = self.get_total_number_of_scrabble_plays()

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

        for where_expression in self._where_expressions:
            query = query.where(where_expression)

        query = query.group_by(ScrabbleWordEntity.text, ScrabbleWordEntity.ngrams_probability)
        query = query.order_by(ScrabbleWordEntity.text)

        return query

    def get_words_and_probabilities(self):
        initialise_database()

        query = self.get_query_for_retrieving_words_and_probabilities()

        words = []
        ngrams_probabilities = []
        scrabble_probabilities = []

        for row in query:
            words.append(row.text)
            ngrams_probabilities.append(row.ngrams_probability)
            scrabble_probabilities.append(row.scrabble_probability)

        return words, ngrams_probabilities, scrabble_probabilities

    def get_total_number_of_scrabble_plays(self):
        initialise_database()

        query = (
            ScrabbleGameWordEntity
            .select(fn.SUM(ScrabbleGameWordEntity.count))
            .join(ScrabbleGameEntity, on=(ScrabbleGameWordEntity.scrabble_game_id == ScrabbleGameEntity.id))
            .join(ScrabbleWordEntity, on=(ScrabbleGameWordEntity.scrabble_word_id == ScrabbleWordEntity.id))
        )

        for where_expression in self._where_expressions:
            query = query.where(where_expression)

        return query.scalar() or 0

    def show_plot(self, x_axis_label_for_ngrams_probabilities: str = "",
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
        words, ngrams_probabilities, scrabble_probabilities = self.get_words_and_probabilities()

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
