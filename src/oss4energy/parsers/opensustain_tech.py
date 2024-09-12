"""
Module parsing https://opensustain.tech/
"""

from bs4 import BeautifulSoup

from oss4energy.helpers import sorted_list_of_unique_elements
from oss4energy.parsers import cached_web_get_text
from oss4energy.parsers.github_data_io import (
    GITHUB_URL_BASE,
    split_organisations_repositories_others,
)


def fetch_all_project_urls_from_opensustain_webpage() -> (
    tuple[list[str], list[str], list[str]]
):
    r_text = cached_web_get_text("https://opensustain.tech/")
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(GITHUB_URL_BASE)
    ]

    orgs, repos, others = split_organisations_repositories_others(shortlisted_urls)

    # Ensure unicity of links
    return (
        sorted_list_of_unique_elements(orgs),
        sorted_list_of_unique_elements(repos),
        sorted_list_of_unique_elements(others),
    )
