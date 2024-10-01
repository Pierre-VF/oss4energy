"""
Module to perform basic search
"""

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from oss4energy.nlp.classifiers import tf_idf


def _lower_str(x: str, *args, **kwargs):
    if isinstance(x, str):
        return x.lower()  # remove_stopwords_and_punctuation(x)
    else:
        return ""


class SearchResults:
    def __init__(self, documents: pd.DataFrame) -> None:
        # Ensuring that the required columns exist
        keys = documents.keys()
        for i in ["language", "description", "readme", "latest_update"]:
            assert i in keys

        self.__documents = documents.copy()

    def __reindex(self):
        self.__documents = self.__documents.reset_index(drop=True)

    def refine_by_languages(
        self, languages: list[str], include_none: bool = False
    ) -> None:
        df_i = pd.concat(
            [self.__documents.query(f"language=='{i}'") for i in languages]
        )
        if include_none:
            df_none = self.__documents[
                self.__documents["language"].apply(
                    lambda x: (x is None) or (np.isreal(x) and np.isnan(x))
                )
            ]
            df_i = pd.concat([df_i, df_none])

        self.__documents = df_i
        self.__reindex()

    def refine_by_keyword(
        self, keyword: str, description: bool = True, readme: bool = True
    ) -> None:
        df_i = self.__documents
        f = lambda x: keyword in _lower_str(x)
        k_selected = []
        if description:
            k_selected = k_selected + df_i[df_i["description"].apply(f)].index.to_list()
        if readme:
            k_selected = k_selected + df_i[df_i["readme"].apply(f)].index.to_list()
        k_selected_unique = list(set(k_selected))
        self.__documents = df_i.iloc[k_selected_unique].copy()
        self.__reindex()

    def order_by_relevance(self, keyword: str):
        r_tfidf = tf_idf([_lower_str(i) for i in self.__documents])
        ordered_results = r_tfidf[keyword].sort_values(ascending=False)
        self.__documents = self.__documents.iloc[ordered_results.index]
        self.__reindex()

    def refine_by_active_in_past_year(self):
        t_last = datetime.now(UTC) - timedelta(days=365)
        self.__documents = self.__documents[self.__documents["latest_update"] > t_last]
        self.__reindex()

    @property
    def documents(self) -> pd.DataFrame:
        return self.__documents

    @property
    def n_documents(self) -> int:
        return len(self.__documents)
