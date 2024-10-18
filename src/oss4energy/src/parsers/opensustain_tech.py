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
from oss4energy.src.parsers.gitlab_data_io import GITLAB_URL_BASE


def _url_is_relevant(url: str) -> bool:
    return url.startswith(GITHUB_URL_BASE) or url.startswith(GITLAB_URL_BASE)


def fetch_all_project_urls_from_opensustain_webpage() -> ParsingTargets:
    r_text = cached_web_get_text("https://opensustain.tech/")
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = [i for i in [x.get("href") for x in rs] if _url_is_relevant(i)]

    out = identify_parsing_targets(shortlisted_urls)

    return out


def _f_clean_key(x):
    return x.text.replace("¶", "")


def fetch_categorised_projects_from_from_opensustain_webpage() -> (
    dict[str, dict[str, list[str]]]
):
    """Fetching categorised links to repositories, which can later be used to build classifiers

    :return: categorised list of repositories
    """
    r_text = cached_web_get_text("https://opensustain.tech/")
    b = BeautifulSoup(r_text, features="html.parser")

    # This part is built for the specific page structure at the time of writing (18/10/2024)
    #   and assumes that the information is rolled out in a consistent sequential manner
    d = dict()
    orphan_links = []
    xs = b.findAll(name=["h2", "h3", "li"])
    current_h2 = None
    current_h3 = None
    for i in xs:
        if i.name == "h2":
            current_h2 = _f_clean_key(i)
            if current_h2 not in d.keys():
                d[current_h2] = dict()
        elif i.name == "h3":
            current_h3 = _f_clean_key(i)
            if current_h3 not in d[current_h2].keys():
                d[current_h2][current_h3] = []
        elif i.name == "li":
            links = [j.get("href") for j in i.findAll(name="a")]
            if current_h2 and current_h3:
                if current_h3 not in d[current_h2].keys():
                    d[current_h2][current_h3] = []
                d[current_h2][current_h3] += links
            else:
                orphan_links += links

    # Removing code-irrelevant fields
    for i in ["Contributors", "Artwork and License"]:
        if i in d.keys():
            d.pop(i)

    # Only keeping URLs deemed relevant
    focused_d = {
        k1: {k2: [i for i in v2 if _url_is_relevant(i)] for k2, v2 in v1.items()}
        for k1, v1 in d.items()
    }

    return focused_d
