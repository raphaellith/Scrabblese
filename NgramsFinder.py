"""
Provides a helper class for retrieving collapsed relative match counts from the ngrams.dev API.

See https://ngrams.dev/.
"""

import requests

class NgramsFinder:
    def __init__(self):
        self.request_session = requests.Session()

    def get_collapsed_relative_match_count(self, ngram: str) -> float:
        """
        Retrieves the collapsed relative match count for a given ngram.
        The retrieval is case-insensitive and limited to English corpora.
        :param ngram: The ngram for which to retrieve the collapsed relative match count.
        :return: The collapsed relative match count for the given ngram.
        """
        print("Getting collapsed relative match count for ngram: " + ngram)

        url = f"https://api.ngrams.dev/eng/search?query={ngram}&flags=cr"
        response: requests.Response = self.request_session.get(url)
        response_dict: dict = response.json()
        ngram_results: list = response_dict["ngrams"]

        if not ngram_results:
            return 0

        return ngram_results[0]["relTotalMatchCount"]


if __name__ == '__main__':
    print(NgramsFinder().get_collapsed_relative_match_count("QI"))