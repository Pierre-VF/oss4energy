"""
Sub-package for NLP management
"""

import pandas as pd
import spacy


def _spacy_model() -> spacy.Language:
    # Make sure to synchronise the model with the install in the makefile
    return spacy.load("en_core_web_sm")


def lemmatise(txt: str, model: spacy.Language | None = None) -> list[str]:
    if model is None:
        model = _spacy_model()
    doc = model(txt)
    return [i.lemma_ for i in doc]


def lemmatise_as_str(txt: str, model: spacy.Language | None = None) -> str:
    return " ".join(lemmatise(txt, model=model))


DELIMITING_CHARACTERS = set(
    ["(", ")", ".", ",", ";", "?", "!", "*", "[", "]", "-", "{", "}"]
)


def remove_stopwords_and_punctuation(
    txt: str, model: spacy.Language | None = None
) -> str:
    if model is None:
        model = _spacy_model()

    to_ignore = model.Defaults.stop_words | DELIMITING_CHARACTERS
    doc = model(txt)
    x_words = [str(i) for i in doc]
    words = [i for i in x_words if i not in to_ignore]
    return " ".join(words)


def lemma_count(txt: str, remove_stopwords: bool = True) -> dict[str, int]:
    m = _spacy_model()
    if remove_stopwords:
        fixed_txt = remove_stopwords_and_punctuation(txt, model=m)
    else:
        fixed_txt = txt
    x = lemmatise(fixed_txt, model=m)
    lemmas_to_ignore = m.Defaults.stop_words | DELIMITING_CHARACTERS
    unique_x = [i for i in list(set(x)) if i not in lemmas_to_ignore]
    out = {i: x.count(i) for i in unique_x}
    df = (
        pd.DataFrame(data={"word": list(out.keys()), "counts": list(out.values())})
        .sort_values(by="counts")
        .reset_index(drop=True)
    )
    out = df.set_index("word")["counts"].to_dict()
    return out
