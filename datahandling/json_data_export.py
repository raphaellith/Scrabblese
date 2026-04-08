import json
from datahandling.database_reader import get_data_points


def _export_data_points_to_json(data_points, filepath):
    data = [
        {
            "word": dp.word,
            "scrabble_play_count": dp.scrabble_play_count,
            "ngrams_probability": dp.ngrams_probability
        }
        for dp in data_points
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_data_points_from_listed_games_to_json(file_path):
    data_points = get_data_points(select_listed_games=True, select_unlisted_games=False)
    _export_data_points_to_json(data_points, file_path)

def export_data_points_from_unlisted_games_to_json(file_path):
    data_points = get_data_points(select_listed_games=False, select_unlisted_games=True)
    _export_data_points_to_json(data_points, file_path)
