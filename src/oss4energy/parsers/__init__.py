"""
Module for parsers and web I/O
"""

import time
from dataclasses import dataclass, field

import requests

from oss4energy.database import load_from_database, save_to_database
from oss4energy.helpers import sorted_list_of_unique_elements
from oss4energy.log import log_info

WEB_SESSION = requests.Session()


def _cached_web_get(
    url: str,
    headers: dict | None = None,
    wait_after_web_query: bool = True,
    is_json: bool = True,
) -> dict | str:
    # Uses the cache to ensure that requests are minimised
    out = load_from_database(url, is_json=is_json)
    if out is None:
        log_info(f"Web GET: {url}")
        r = WEB_SESSION.get(
            url=url,
            headers=headers,
        )
        if is_json:
            r.raise_for_status()
            out = r.json()
        else:
            if r.status_code == 404:
                log_info(f"> No resource found for: {url}")
                out = "(None)"
            else:
                r.raise_for_status()
                out = r.text
        save_to_database(url, out, is_json=is_json)
        if wait_after_web_query:
            time.sleep(
                0.1
            )  # To avoid triggering rate limits on APIs and be nice to servers
    else:
        log_info(f"Cache-loading: {url}")
    return out


def cached_web_get_json(
    url: str, headers: dict | None = None, wait_after_web_query: bool = True
) -> dict:
    return _cached_web_get(
        url=url,
        headers=headers,
        wait_after_web_query=wait_after_web_query,
        is_json=True,
    )


def cached_web_get_text(
    url: str, headers: dict | None = None, wait_after_web_query: bool = True
) -> str:
    return _cached_web_get(
        url=url,
        headers=headers,
        wait_after_web_query=wait_after_web_query,
        is_json=False,
    )


@dataclass
class ParsingTargetSet:
    github_repositories: list[str] = field(default_factory=[])
    github_organisations: list[str] = field(default_factory=[])
    unknown: list[str] = field(default_factory=[])

    def __add__(self, other: "ParsingTargetSet") -> "ParsingTargetSet":
        return ParsingTargetSet(
            github_organisations=self.github_organisations + other.github_organisations,
            github_repositories=self.github_repositories + other.github_repositories,
            unknown=self.unknown + other.unknown,
        )

    def __iadd__(self, other: "ParsingTargetSet") -> "ParsingTargetSet":
        self.github_repositories += other.github_repositories
        self.github_organisations += other.github_organisations
        self.unknown += other.unknown
        return self

    def ensure_sorted_and_unique_elements(self) -> None:
        self.github_repositories = sorted_list_of_unique_elements(
            self.github_repositories
        )
        self.github_organisations = sorted_list_of_unique_elements(
            self.github_organisations
        )
        self.unknown = sorted_list_of_unique_elements(self.unknown)
