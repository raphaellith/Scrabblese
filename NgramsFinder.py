import requests

class NgramsFinder:
    def __init__(self):
        self.request_session = requests.Session()

    def get_collapsed_relative_match_count(self, ngram: str) -> float:
        url = f"https://api.ngrams.dev/eng/search?query={ngram}&flags=cr"
        response: requests.Response = self.request_session.get(url)
        response_dict: dict = response.json()
        return response_dict["ngrams"][0]["relTotalMatchCount"]


if __name__ == '__main__':
    print(NgramsFinder().get_collapsed_relative_match_count("QI"))