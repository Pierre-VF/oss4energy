import pytest


# Github fixtures
@pytest.fixture
def github_repo_url() -> str:
    return "https://github.com/Pierre-VF/oss4energy"


@pytest.fixture
def github_organisation_url() -> str:
    return "https://github.com/carbon-data-specification"


# Gitlab fixtures
@pytest.fixture
def gitlab_repo_url() -> str:
    return "https://gitlab.com/polito-edyce-prelude/predyce"


@pytest.fixture
def gitlab_group_url() -> str:
    return "https://gitlab.com/polito-edyce-prelude"
