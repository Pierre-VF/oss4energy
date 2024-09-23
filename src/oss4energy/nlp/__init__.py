"""
Sub-package for NLP management
"""

import spacy


def _spacy_model() -> spacy.Language:
    # MAke sure to synchronise the modle with the install in the makefile
    return spacy.load("en_core_web_sm")


def lemmatise(txt: str) -> str:
    m = _spacy_model()
    doc = m(txt)
    lemmatised_doc = " ".join([i.lemma_ for i in doc])
    return lemmatised_doc
