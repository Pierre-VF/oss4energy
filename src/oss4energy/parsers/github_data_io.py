from datetime import datetime

from oss4energy.config import SETTINGS
from oss4energy.model import ProjectDetails
from oss4energy.parsers import cached_web_get_json


def _process_url_if_needed(x: str) -> str:
    full_url_prefix = "https://github.com/"
    if x.startswith(full_url_prefix):
        x = x.replace(full_url_prefix, "")
    return x


def web_get(url: str, authorise: bool) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if authorise:
        headers["Authorization"] = f"Bearer {SETTINGS.GITHUB_API_TOKEN}"
    res = cached_web_get_json(url=url, headers=headers)
    return res


def fetch_repositories_in_organisation(organisation_name: str) -> dict[str, str]:
    organisation_name = _process_url_if_needed(organisation_name)

    res = web_get(
        f"https://api.github.com/orgs/{organisation_name}/repos", authorise=False
    )
    return {r["name"]: r["html_url"] for r in res}


def fetch_repository_details(repo_path: str) -> ProjectDetails:
    repo_path = _process_url_if_needed(repo_path)

    r = web_get(f"https://api.github.com/repos/{repo_path}", authorise=False)

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
