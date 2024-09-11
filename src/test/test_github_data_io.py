from oss4energy.parsers.github_data_io import (
    ProjectDetails,
    fetch_repositories_in_organisation,
    fetch_repository_details,
)


def test_fetch_functions(github_repo_url, github_organisation_url):
    res_repo = fetch_repository_details(github_repo_url)
    assert isinstance(res_repo, ProjectDetails)

    res_org = fetch_repositories_in_organisation(github_organisation_url)
    assert isinstance(res_org, dict)

    print("ok")
