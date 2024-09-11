from datetime import datetime
from enum import Enum
from functools import lru_cache

from oss4energy.config import SETTINGS
from oss4energy.log import log_info
from oss4energy.model import ProjectDetails
from oss4energy.parsers import cached_web_get_json, cached_web_get_text


def _process_url_if_needed(x: str) -> str:
    full_url_prefix = "https://github.com/"
    if x.startswith(full_url_prefix):
        x = x.replace(full_url_prefix, "")
    if x.endswith("/"):
        x = x[:-1]
    return x


class GithubTargetType(Enum):
    ORGANISATION = "ORGANISATION"
    REPOSITORY = "REPOSITORY"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def identify(url: str) -> "GithubTargetType":
        processed = _process_url_if_needed(url)
        n_slashes = processed.count("/")
        if n_slashes < 1:
            return GithubTargetType.ORGANISATION
        elif n_slashes == 1:
            return GithubTargetType.REPOSITORY
        else:
            return GithubTargetType.UNKNOWN


@lru_cache(maxsize=1)
def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if SETTINGS.GITHUB_API_TOKEN is None:
        log_info("Github running in PUBLIC mode")
    else:
        log_info("Github running in AUTHENTICATED mode")
        headers["Authorization"] = f"Bearer {SETTINGS.GITHUB_API_TOKEN}"
    return headers


def web_get(url: str, with_headers: bool = True, is_json: bool = True) -> dict:
    if with_headers:
        headers = _github_headers()
    else:
        headers = None
    if is_json:
        res = cached_web_get_json(url=url, headers=headers)
    else:
        res = cached_web_get_text(url=url, headers=headers)
    return res


def fetch_repositories_in_organisation(organisation_name: str) -> dict[str, str]:
    organisation_name = _process_url_if_needed(organisation_name)

    res = web_get(
        f"https://api.github.com/orgs/{organisation_name}/repos",
    )
    return {r["name"]: r["html_url"] for r in res}


def fetch_repository_details(repo_path: str) -> ProjectDetails:
    repo_path = _process_url_if_needed(repo_path)

    r = web_get(f"https://api.github.com/repos/{repo_path}")

    license = r["license"]
    if license is not None:
        license = r["name"]

    details = ProjectDetails(
        name=r["name"],
        url=r["html_url"],
        website=r["homepage"],
        description=r["description"],
        license=license,
        language=r["language"],
        latest_update=datetime.fromisoformat(r["updated_at"]),
        raw_details=r,
    )
    return details


def fetch_repository_readme(repository_url: str) -> str | None:
    repo_name = _process_url_if_needed(repository_url)
    try:
        md_content = web_get(
            f"https://raw.githubusercontent.com/{repo_name}/main/README.md",
            with_headers=None,
            is_json=False,
        )
    except Exception as e:
        md_content = f"ERROR with README.md ({e})"

    return md_content
