import requests

SESSION = requests.Session()


def _process_url_if_needed(x: str) -> str:
    full_url_prefix = "https://github.com/"
    if x.startswith(full_url_prefix):
        x = x.replace(full_url_prefix, "")
    return x


def web_get(url, authorise: bool) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if authorise:
        from oss4energy.config import SETTINGS

        headers["Authorization"] = f"Bearer {SETTINGS.GITHUB_API_TOKEN}"

    r = SESSION.get(
        url=url,
        headers=headers,
    )
    r.raise_for_status()
    return r.json()


def fetch_repositories_in_organisation(organisation_name: str):
    organisation_name = _process_url_if_needed(organisation_name)

    r = web_get(
        f"https://api.github.com/orgs/{organisation_name}/repos", authorise=False
    )
    # TODO : proper parsing remains to be done
    return r


def fetch_repository_details(repo_path: str):
    repo_path = _process_url_if_needed(repo_path)

    r = web_get(f"https://api.github.com/repos/{repo_path}", authorise=False)
    # TODO : proper parsing remains to be done
    return r


if __name__ == "__main__":
    r1 = fetch_repositories_in_organisation(
        "https://github.com/carbon-data-specification"
    )
    r1 = fetch_repository_details()
