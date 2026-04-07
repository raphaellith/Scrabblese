"""
A template program for retrieving and plotting data points from the database.
"""

from matplotlib import pyplot as plt
from datahandling.database_reader import get_data_points


data_points = get_data_points(select_listed_games=True, select_unlisted_games=False)

data_points = [d for d in data_points if len(d.word) == 2]

plt.scatter([d.ngrams_probability for d in data_points], [d.scrabble_play_count for d in data_points], marker=".")

plt.xscale("log")
plt.yscale("log")

for d in data_points:
    plt.annotate(d.word, (d.ngrams_probability, d.scrabble_play_count))

plt.xlabel("Ngrams probability")
plt.ylabel("Scrabble play count")
plt.show()
