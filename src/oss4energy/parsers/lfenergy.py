"""
Parser for LF Energy projects
"""

from bs4 import BeautifulSoup

from oss4energy.parsers import WEB_SESSION

from .github_data_io import GithubTargetType

_PROJECT_PAGE_URL_BASE = "https://lfenergy.org/projects/"


def fetch_all_project_urls() -> list[str]:
    r = WEB_SESSION.get("https://lfenergy.org/our-projects/")
    r.raise_for_status()
    b = BeautifulSoup(r.text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(_PROJECT_PAGE_URL_BASE)
    ]
    # Ensure unicity of links
    return list(set(shortlisted_urls))


def fetch_project_github_urls(
    project_url: str,
) -> tuple[list[str], list[str], list[str]]:
    if not project_url.startswith(_PROJECT_PAGE_URL_BASE):
        raise ValueError(f"Unsupported page URL ({project_url})")
    r = WEB_SESSION.get(project_url)
    r.raise_for_status()
    b = BeautifulSoup(r.text, features="html.parser")

    rs = b.findAll(name="a", attrs={"class": "projects-icon"})
    github_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith("https://github.com/")
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
