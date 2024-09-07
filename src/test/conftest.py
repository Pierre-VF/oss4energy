import pytest


@pytest.fixture
def github_repo_url() -> str:
    return "https://github.com/Pierre-VF/website_scanner"


@pytest.fixture
def github_organisation_url() -> str:
    return "https://github.com/carbon-data-specification"
