"""
Module to manage parsing of Gitlab data

Note:
- Doc: https://docs.gitlab.com/ee/api/projects.html#get-a-single-project
- Personal access token: https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
"""

from datetime import datetime
from enum import Enum
from functools import lru_cache
from urllib.parse import quote_plus

from oss4energy.src.config import SETTINGS
from oss4energy.src.log import log_info
from oss4energy.src.model import ProjectDetails
from oss4energy.src.parsers import (
    ParsingTargets,
    cached_web_get_json,
    cached_web_get_text,
)

GITLAB_URL_BASE = "https://gitlab.com/"


def _extract_organisation_and_repository_as_url_block(x: str) -> str:
    # Cleaning up Github prefix
    if x.startswith(GITLAB_URL_BASE):
        x = x.replace(GITLAB_URL_BASE, "")
    # Removing eventual extra information in URL
    for i in ["#", "&"]:
        if i in x:
            x = x.split(i)[0]
    # Removing trailing "/", if any
    while x.endswith("/"):
        x = x[:-1]
    return x


@lru_cache(maxsize=1)
def _gitlab_headers() -> dict[str, str]:
    if SETTINGS.GITLAB_ACCESS_TOKEN is None:
        log_info("Gitlab running in PUBLIC mode")
    else:
        log_info("Gitlab running in AUTHENTICATED mode")
        headers = {
            "PRIVATE-TOKEN": SETTINGS.GITLAB_ACCESS_TOKEN,
        }
    return headers


def _web_get(url: str, with_headers: bool = True, is_json: bool = True) -> dict:
    if with_headers:
        headers = _gitlab_headers()
    else:
        headers = None
    if is_json:
        res = cached_web_get_json(url=url, headers=headers)
    else:
        res = cached_web_get_text(url=url, headers=headers)
    return res


def fetch_repository_details(repo_path: str) -> ProjectDetails:
    repo_id = _extract_organisation_and_repository_as_url_block(repo_path)

    url = f"https://gitlab.com/api/v4/projects/{quote_plus(repo_id)}"

    r = _web_get(url, is_json=True)

    organisation = r["namespace"]["name"]
    license = "?"  # TODO : need to find how to parse the licence of a project
    url_open_pr = r["_links"]["merge_requests"]
    r_open_pr = _web_get(url_open_pr, is_json=True)
    n_open_prs = len([i for i in r_open_pr if i.get("state") == "open"])

    details = ProjectDetails(
        id=repo_path,
        name=r["name"],
        organisation=organisation,
        url=r["web_url"],
        website=None,
        description=r["description"],
        license=license,
        language=None,  # Not available
        latest_update=datetime.fromisoformat(r["updated_at"]),
        last_commit=datetime.fromisoformat(r["last_activity_at"]),
        open_pull_requests=n_open_prs,
        raw_details=r,
        master_branch=r["default_branch"],
    )
    return details


def fetch_repository_readme(repository_url: str) -> str | None:
    repo_name = _extract_organisation_and_repository_as_url_block(repository_url)
    try:
        md_content = _web_get(
            f"https://raw.githubusercontent.com/{repo_name}/main/README.md",
            with_headers=None,
            is_json=False,
        )
    except Exception as e:
        md_content = f"ERROR with README.md ({e})"

    return md_content


class GitlabTargetType(Enum):
    GROUP = "GROUP"
    REPOSITORY = "REPOSITORY"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def identify(url: str) -> "GitlabTargetType":
        if not url.startswith(GITLAB_URL_BASE):
            return GitlabTargetType.UNKNOWN
        processed = _extract_organisation_and_repository_as_url_block(url)
        n_slashes = processed.count("/")
        if n_slashes < 1:
            return GitlabTargetType.GROUP
        elif n_slashes >= 1:
            return GitlabTargetType.REPOSITORY
        else:
            return GitlabTargetType.UNKNOWN


def split_across_target_sets(
    x: list[str],
) -> ParsingTargets:
    groups = []
    repos = []
    others = []
    for i in x:
        tt_i = GitlabTargetType.identify(i)
        if tt_i is GitlabTargetType.GROUP:
            groups.append(i)
        elif tt_i is GitlabTargetType.REPOSITORY:
            repos.append(i)
        else:
            others.append(i)

    # Orgs are not yet parsed
    unknown = others + groups

    return ParsingTargets(gitlab_repositories=repos, unknown=unknown)


if __name__ == "__main__":
    r0 = fetch_repository_details("https://gitlab.com/polito-edyce-prelude/predyce")
    print(r0)
