from datetime import datetime
from enum import Enum
from functools import lru_cache

from oss4energy.src.config import SETTINGS
from oss4energy.src.log import log_info
from oss4energy.src.model import ProjectDetails
from oss4energy.src.parsers import (
    ParsingTargets,
    cached_web_get_json,
    cached_web_get_text,
)

GITHUB_URL_BASE = "https://github.com/"


def extract_organisation_and_repository_as_url_block(x: str) -> str:
    # Cleaning up Github prefix
    if x.startswith(GITHUB_URL_BASE):
        x = x.replace(GITHUB_URL_BASE, "")
    # Removing eventual extra information in URL
    for i in ["#", "&"]:
        if i in x:
            x = x.split(i)[0]
    # Removing trailing "/", if any
    while x.endswith("/"):
        x = x[:-1]
    return x


class GithubTargetType(Enum):
    ORGANISATION = "ORGANISATION"
    REPOSITORY = "REPOSITORY"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def identify(url: str) -> "GithubTargetType":
        processed = extract_organisation_and_repository_as_url_block(url)
        n_slashes = processed.count("/")
        if n_slashes < 1:
            return GithubTargetType.ORGANISATION
        elif n_slashes == 1:
            return GithubTargetType.REPOSITORY
        else:
            return GithubTargetType.UNKNOWN


def split_across_target_sets(
    x: list[str],
) -> ParsingTargets:
    orgs = []
    repos = []
    others = []
    for i in x:
        tt_i = GithubTargetType.identify(i)
        if tt_i is GithubTargetType.ORGANISATION:
            orgs.append(i)
        elif tt_i is GithubTargetType.REPOSITORY:
            repos.append(i)
        else:
            others.append(i)
    return ParsingTargets(
        github_organisations=orgs, github_repositories=repos, unknown=others
    )


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


def _web_get(url: str, with_headers: bool = True, is_json: bool = True) -> dict:
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
    organisation_name = extract_organisation_and_repository_as_url_block(
        organisation_name
    )

    res = _web_get(
        f"https://api.github.com/orgs/{organisation_name}/repos",
    )
    return {r["name"]: r["html_url"] for r in res}


def _master_branch_name(cleaned_repo_path: str) -> str | None:
    # Gather extra metadata
    r_branches = _web_get(f"https://api.github.com/repos/{cleaned_repo_path}/branches")
    branches_names = [i["name"] for i in r_branches]
    if "main" in branches_names:
        branch2use = "main"
    elif "master" in branches_names:
        branch2use = "master"
    else:
        log_info(f"Unable to select branch among: {branches_names}")
        branch2use = None
    return branch2use


def fetch_repository_details(repo_path: str) -> ProjectDetails:
    repo_path = extract_organisation_and_repository_as_url_block(repo_path)

    r = _web_get(f"https://api.github.com/repos/{repo_path}")
    branch2use = _master_branch_name(repo_path)

    if branch2use is None:
        last_commit = None
    else:
        r_last_commit_to_master = _web_get(
            f"https://api.github.com/repos/{repo_path}/commits/{branch2use}"
        )
        last_commit = datetime.fromisoformat(
            r_last_commit_to_master["commit"]["author"]["date"]
        )

    r_pull_requests = _web_get(f"https://api.github.com/repos/{repo_path}/pulls")

    n_open_pull_requests = len([i for i in r_pull_requests if i["state"] == "open"])

    organisation = repo_path.split("/")[0]

    license = r["license"]
    if license is not None:
        license = license["name"]

    details = ProjectDetails(
        id=repo_path,
        name=r["name"],
        organisation=organisation,
        url=r["html_url"],
        website=r["homepage"],
        description=r["description"],
        license=license,
        language=r["language"],
        latest_update=datetime.fromisoformat(r["updated_at"]),
        last_commit=last_commit,
        open_pull_requests=n_open_pull_requests,
        raw_details=r,
    )
    return details


def fetch_repository_readme(repository_url: str) -> str | None:
    repo_name = extract_organisation_and_repository_as_url_block(repository_url)
    try:
        md_content = _web_get(
            f"https://raw.githubusercontent.com/{repo_name}/main/README.md",
            with_headers=None,
            is_json=False,
        )
    except Exception as e:
        md_content = f"ERROR with README.md ({e})"

    return md_content


def fetch_repository_file_tree(repository_url: str) -> list[str] | str:
    repo_name = extract_organisation_and_repository_as_url_block(repository_url)
    branch = _master_branch_name(repo_name)
    if branch is None:
        return "ERROR with file tree (unclear master branch)"
    try:
        r = _web_get(
            url=f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1",
            with_headers=None,
            is_json=True,
        )
        file_tree = [i["path"] for i in r["tree"]]
    except Exception as e:
        file_tree = f"ERROR with file tree ({e})"
    return file_tree


if __name__ == "__main__":
    r = fetch_repository_file_tree("https://github.com/Pierre-VF/oss4energy/")
    print("Done")
