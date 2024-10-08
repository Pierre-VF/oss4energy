"""
Module parsing https://opensustain.tech/
"""

from bs4 import BeautifulSoup

from oss4energy.src.parsers import (
    ParsingTargets,
    cached_web_get_text,
    identify_parsing_targets,
)
from oss4energy.src.parsers.github_data_io import GITHUB_URL_BASE


def fetch_all_project_urls_from_opensustain_webpage() -> ParsingTargets:
    r_text = cached_web_get_text("https://opensustain.tech/")
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(GITHUB_URL_BASE)
    ]

    out = identify_parsing_targets(shortlisted_urls)

    return out
