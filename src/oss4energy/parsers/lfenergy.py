"""
Parser for LF Energy projects
"""

import yaml
from bs4 import BeautifulSoup

from oss4energy.helpers import sorted_list_of_unique_elements
from oss4energy.parsers import cached_web_get_text
from oss4energy.parsers.github_data_io import GITHUB_URL_BASE, GithubTargetType

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
) -> tuple[list[str], list[str], list[str]]:
    if not project_url.startswith(_PROJECT_PAGE_URL_BASE):
        raise ValueError(f"Unsupported page URL ({project_url})")
    r_text = cached_web_get_text(project_url)
    b = BeautifulSoup(r_text, features="html.parser")

    rs = b.findAll(name="a", attrs={"class": "projects-icon"})
    github_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(GITHUB_URL_BASE)
    ]
    github_urls = [i for i in github_urls if not i.endswith(".md")]
    organisations = []
    repositories = []
    unknowns = []
    for i in github_urls:
        tt_i = GithubTargetType.identify(i)
        if tt_i is GithubTargetType.ORGANISATION:
            organisations.append(i)
        elif tt_i is GithubTargetType.REPOSITORY:
            repositories.append(i)
        else:
            unknowns.append(i)
    return organisations, repositories, unknowns


def get_open_source_energy_projects_from_landscape() -> tuple[list[str], list[str]]:
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
            # for ssc in _list_if_exists(sc, "subcategories"):
            for i in _list_if_exists(sc, "items"):
                repo_url = i.get("repo_url")
                if repo_url:
                    repos.append(repo_url)

    github_repos = [
        i
        for i in sorted_list_of_unique_elements(repos)
        if i.startswith(GITHUB_URL_BASE)
    ]
    other_repos = [
        i
        for i in sorted_list_of_unique_elements(repos)
        if not i.startswith(GITHUB_URL_BASE)
    ]

    return github_repos, other_repos


if __name__ == "__main__":
    r = get_open_source_energy_projects_from_landscape()
    print(r)
