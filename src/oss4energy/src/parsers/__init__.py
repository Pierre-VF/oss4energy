"""
Module for parsers and web I/O
"""

import re
import time
from dataclasses import dataclass, field

import requests
import tomllib
from bs4 import BeautifulSoup
from tomlkit import document, dump

from oss4energy.src.database import load_from_database, save_to_database
from oss4energy.src.helpers import sorted_list_of_unique_elements
from oss4energy.src.log import log_info

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
class ParsingTargets:
    """
    Class to make aggregation of parsings across targets easier to manage and work with
    """

    github_repositories: list[str] = field(default_factory=list)
    github_organisations: list[str] = field(default_factory=list)
    gitlab_repositories: list[str] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)
    invalid: list[str] = field(default_factory=list)

    def __add__(self, other: "ParsingTargets") -> "ParsingTargets":
        return ParsingTargets(
            github_organisations=self.github_organisations + other.github_organisations,
            github_repositories=self.github_repositories + other.github_repositories,
            gitlab_repositories=self.gitlab_repositories + other.gitlab_repositories,
            unknown=self.unknown + other.unknown,
            invalid=self.invalid + other.invalid,
        )

    def __iadd__(self, other: "ParsingTargets") -> "ParsingTargets":
        self.github_repositories += other.github_repositories
        self.github_organisations += other.github_organisations
        self.gitlab_repositories += other.gitlab_repositories
        self.unknown += other.unknown
        self.invalid += other.invalid
        return self

    def as_url_list(self, known_repositories_only: bool = True) -> list[str]:
        out = self.github_repositories + self.gitlab_repositories
        if not known_repositories_only:
            out += self.github_organisations + self.unknown + self.invalid
        return out

    def ensure_sorted_and_unique_elements(self) -> None:
        """
        Sorts all fields alphabetically and ensures that there is no redundancies in them
        """
        self.github_repositories = sorted_list_of_unique_elements(
            self.github_repositories
        )
        self.github_organisations = sorted_list_of_unique_elements(
            self.github_organisations
        )
        self.gitlab_repositories = sorted_list_of_unique_elements(
            self.gitlab_repositories
        )
        self.unknown = sorted_list_of_unique_elements(self.unknown)
        self.invalid = sorted_list_of_unique_elements(self.invalid)

    @staticmethod
    def from_toml(toml_file_path: str) -> "ParsingTargets":
        if not toml_file_path.endswith(".toml"):
            raise ValueError("Input must be a TOML file")

        with open(toml_file_path, "rb") as f:
            x = tomllib.load(f)

        return ParsingTargets(
            github_organisations=x["github_hosted"].get("organisations", []),
            github_repositories=x["github_hosted"].get("repositories", []),
            gitlab_repositories=x["gitlab_hosted"].get("repositories", []),
            unknown=x["dropped_targets"].get("urls", []),
            invalid=x["dropped_targets"].get("invalid_urls", []),
        )

    def to_toml(self, toml_file_path: str) -> None:
        if not toml_file_path.endswith(".toml"):
            raise ValueError("Output must be a TOML file")

        # Outputting to a new TOML
        doc = document()
        toml_ready_dict = {
            "github_hosted": {
                "organisations": self.github_organisations,
                "repositories": self.github_repositories,
            },
            "gitlab_hosted": {
                "repositories": self.gitlab_repositories,
            },
            "dropped_targets": {
                "urls": self.unknown,
                "invalid_urls": self.invalid,
            },
        }

        for k, v in toml_ready_dict.items():
            doc.add(k, v)

        with open(toml_file_path, "w") as fp:
            dump(doc, fp, sort_keys=True)


def identify_parsing_targets(x: list[str]) -> ParsingTargets:
    from oss4energy.src.parsers import github_data_io, gitlab_data_io

    out_github = github_data_io.split_across_target_sets(x)
    out_gitlab = gitlab_data_io.split_across_target_sets(out_github.unknown)
    out_github.unknown = []

    out = out_github + out_gitlab
    return out


def isolate_relevant_urls(urls: list[str]) -> list[str]:
    from oss4energy.src.parsers.github_data_io import GITHUB_URL_BASE
    from oss4energy.src.parsers.gitlab_data_io import GITLAB_URL_BASE

    def __f(i) -> bool:
        if i.startswith(GITHUB_URL_BASE):
            if (
                ("/tree/" in i) or ("/blob/" in i) or i.endswith("/releases")
            ):  # To avoid file detection leading to clutter
                return False
            else:
                return True
        elif i.startswith(GITLAB_URL_BASE):
            return True
        else:
            return False

    return [x for x in urls if __f(x)]


# For listings
@dataclass
class ResourceListing:
    """
    Class to make listings easier to work with
    """

    # For compatibility, all these repo must have data in the README
    github_readme_listings: list[str] = field(default_factory=list)

    # For the links must be given as hrefs in "a" tags
    webpage_html: list[str] = field(default_factory=list)

    # Faults
    fault_urls: list[str] = field(default_factory=list)
    fault_invalid_urls: list[str] = field(default_factory=list)

    def __add__(self, other: "ResourceListing") -> "ResourceListing":
        return ResourceListing(
            github_readme_listings=self.github_readme_listings
            + other.github_readme_listings,
            webpage_html=self.webpage_html + other.webpage_html,
            fault_urls=self.fault_urls + other.fault_urls,
            fault_invalid_urls=self.fault_invalid_urls + other.fault_invalid_urls,
        )

    def __iadd__(self, other: "ResourceListing") -> "ResourceListing":
        self.github_readme_listings += other.github_readme_listings
        self.webpage_html += other.webpage_html
        self.fault_urls += other.fault_urls
        self.fault_invalid_urls += other.fault_invalid_urls
        return self

    def ensure_sorted_and_unique_elements(self) -> None:
        """
        Sorts all fields alphabetically and ensures that there is no redundancies in them
        """
        self.github_readme_listings = sorted_list_of_unique_elements(
            self.github_readme_listings
        )
        self.webpage_html = sorted_list_of_unique_elements(self.webpage_html)
        self.fault_urls = sorted_list_of_unique_elements(self.fault_urls)
        self.fault_invalid_urls = sorted_list_of_unique_elements(
            self.fault_invalid_urls
        )

    @staticmethod
    def from_toml(toml_file_path: str) -> "ResourceListing":
        if not toml_file_path.endswith(".toml"):
            raise ValueError("Input must be a TOML file")

        with open(toml_file_path, "rb") as f:
            x = tomllib.load(f)

        return ResourceListing(
            github_readme_listings=x["github_hosted"].get("readme_listings", []),
            webpage_html=x["webpages"].get("html", []),
            fault_urls=x["faults"].get("urls", []),
            fault_invalid_urls=x["faults"].get("invalid_urls", []),
        )

    def to_toml(self, toml_file_path: str) -> None:
        if not toml_file_path.endswith(".toml"):
            raise ValueError("Output must be a TOML file")

        # Outputting to a new TOML
        doc = document()
        toml_ready_dict = {
            "github_hosted": {
                "readme_listings": self.github_readme_listings,
            },
            "webpages": {
                "html": self.webpage_html,
            },
            "faults": {
                "urls": self.fault_urls,
                "invalid_urls": self.fault_invalid_urls,
            },
        }

        for k, v in toml_ready_dict.items():
            doc.add(k, v)

        with open(toml_file_path, "w") as fp:
            dump(doc, fp, sort_keys=True)


def fetch_all_project_urls_from_html_webpage(url: str) -> ParsingTargets:
    r_text = cached_web_get_text(url)
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = isolate_relevant_urls([x.get("href") for x in rs])
    return identify_parsing_targets(shortlisted_urls)


def find_links_in_markdown(markdown_text: str) -> list[str]:
    pattern = r"\[([^\]]+)\]\(([^\)]+)\)|\[([^\]]+)\]\s*\[([^\]]*)\]"
    out = re.findall(pattern, markdown_text)
    return [i[1] for i in out]


def fetch_all_project_urls_from_markdown_str(markdown_text: str) -> ParsingTargets:
    r = find_links_in_markdown(markdown_text)
    shortlisted_urls = isolate_relevant_urls(r)
    return identify_parsing_targets(shortlisted_urls)
