"""
Parser for LF Energy projects
"""

import yaml
from bs4 import BeautifulSoup

from oss4energy.src.parsers import ParsingTargets, cached_web_get_text
from oss4energy.src.parsers.github_data_io import (
    GITHUB_URL_BASE,
    split_across_target_sets,
)

_PROJECT_PAGE_URL_BASE = "https://lfenergy.org/projects/"


def fetch_all_project_urls_from_lfe_webpage() -> list[str]:
    r_text = cached_web_get_text("https://lfenergy.org/our-projects/")
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(_PROJECT_PAGE_URL_BASE)
    ]
    # Ensure unicity of links
    return list(set(shortlisted_urls))


def fetch_project_github_urls_from_lfe_energy_project_webpage(
    project_url: str,
) -> ParsingTargets:
    if not project_url.startswith(_PROJECT_PAGE_URL_BASE):
        raise ValueError(f"Unsupported page URL ({project_url})")
    r_text = cached_web_get_text(project_url)
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a", attrs={"class": "projects-icon"})
    github_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(GITHUB_URL_BASE)
    ]
    github_urls = [i for i in github_urls if not i.endswith(".md")]
    return split_across_target_sets(github_urls)


def get_open_source_energy_projects_from_landscape() -> ParsingTargets:
    r = cached_web_get_text(
        "https://raw.githubusercontent.com/lf-energy/lfenergy-landscape/main/landscape.yml"
    )
    out = yaml.load(r, Loader=yaml.CLoader)

    def _list_if_exists(x, k):
        v = x.get(k)
        if v is None:
            return []
        else:
            return v

    repos = []
    for x in _list_if_exists(out, "landscape"):
        for sc in _list_if_exists(x, "subcategories"):
            for i in _list_if_exists(sc, "items"):
                repo_url = i.get("repo_url")
                if repo_url:
                    repos.append(repo_url)

    return split_across_target_sets(repos)
