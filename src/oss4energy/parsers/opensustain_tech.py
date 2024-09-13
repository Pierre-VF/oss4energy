"""
Module parsing https://opensustain.tech/
"""

from bs4 import BeautifulSoup

from oss4energy.parsers import ParsingTargetSet, cached_web_get_text
from oss4energy.parsers.github_data_io import (
    GITHUB_URL_BASE,
    split_across_target_sets,
)


def fetch_all_project_urls_from_opensustain_webpage() -> ParsingTargetSet:
    r_text = cached_web_get_text("https://opensustain.tech/")
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(GITHUB_URL_BASE)
    ]

    out = split_across_target_sets(shortlisted_urls)

    return out
