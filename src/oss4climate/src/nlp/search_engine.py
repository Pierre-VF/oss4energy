"""
A minimal search engine implementation

Taken from https://github.com/alexmolas/microsearch/blob/main/src/microsearch/engine.py
"""

import string
from collections import defaultdict
from math import log

import pandas as pd


def update_url_scores(old: dict[str, float], new: dict[str, float]):
    for url, score in new.items():
        if url in old:
            old[url] += score
        else:
            old[url] = score
    return old


def normalize_string(input_string: str) -> str:
    translation_table = str.maketrans(string.punctuation, " " * len(string.punctuation))
    string_without_punc = input_string.translate(translation_table)
    string_without_double_spaces = " ".join(string_without_punc.split())
    return string_without_double_spaces.lower()


class SearchEngine:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self._index: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._documents: dict[str, str] = {}
        self.k1 = k1
        self.b = b

    @property
    def posts(self) -> list[str]:
        return list(self._documents.keys())

    @property
    def number_of_documents(self) -> int:
        return len(self._documents)

    @property
    def avdl(self) -> float:
        if not hasattr(self, "_avdl"):
            self._avdl = sum(len(d) for d in self._documents.values()) / len(
                self._documents
            )
        return self._avdl

    def idf(self, kw: str) -> float:
        N = self.number_of_documents
        n_kw = len(self.get_urls(kw))
        return log((N - n_kw + 0.5) / (n_kw + 0.5) + 1)

    def bm25(self, kw: str) -> dict[str, float]:
        result = {}
        idf_score = self.idf(kw)
        avdl = self.avdl
        for url, freq in self.get_urls(kw).items():
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (
                1 - self.b + self.b * len(self._documents[url]) / avdl
            )
            result[url] = idf_score * numerator / denominator
        return result

    def search(self, query: str) -> dict[str, float]:
        keywords = normalize_string(query).split(" ")
        url_scores: dict[str, float] = {}
        for kw in keywords:
            kw_urls_score = self.bm25(kw)
            url_scores = update_url_scores(url_scores, kw_urls_score)
        return pd.Series(list(url_scores.values()), index=list(url_scores.keys()))

    def index(self, url: str, content: str) -> None:
        self._documents[url] = content
        words = normalize_string(content).split(" ")
        for word in words:
            self._index[word][url] += 1
        if hasattr(self, "_avdl"):
            del self._avdl

    def bulk_index(self, documents: list[tuple[str, str]]):
        for url, content in documents:
            self.index(url, content)

    def get_urls(self, keyword: str) -> dict[str, int]:
        keyword = normalize_string(keyword)
        return self._index[keyword]


if __name__ == "__main__":
    from tqdm import tqdm

    from oss4climate.scripts import (
        FILE_OUTPUT_LISTING_FEATHER,
    )
    from oss4climate.src.nlp.search import SearchResults

    x = SearchResults(FILE_OUTPUT_LISTING_FEATHER)
    df = x.documents

    search_engine_description = SearchEngine()
    search_engine_readme = SearchEngine()
    for i, r in tqdm(df.iterrows()):
        # Skip repos with missing info
        if r["readme"] is None:
            continue
        if r["description"] is None:
            continue
        search_engine_description.index(url=r["url"], content=r["description"])
        search_engine_readme.index(r["url"], content=r["readme"])

    res_desc = search_engine_description.search("pv inverter solar")
    res_readme = search_engine_readme.search("pv inverter solar")

    df_combined = (
        res_desc.to_frame("description")
        .merge(
            res_readme.to_frame("readme"),
            how="outer",
            left_index=True,
            right_index=True,
        )
        .fillna(0)
    )

    df_combined["ranking"] = df_combined["description"] * 10 + df_combined["readme"]

    df_out = df.merge(
        df_combined.sort_values(by="ranking", ascending=False),
        how="right",
        left_on="url",
        right_index=True,
    )

    print("x")
