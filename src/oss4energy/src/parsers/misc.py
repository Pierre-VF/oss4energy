"""
Module parsing https://github.com/github/GreenSoftwareDirectory
"""

from oss4energy.src.parsers import (
    ParsingTargets,
    github_data_io,
)
from oss4energy.src.parsers import (
    fetch_all_project_urls_from_markdown_str as __fetch_from_markdown_str,
)


def fetch_all() -> ParsingTargets:
    """Convenience call for all the below

    :return: sum of all listings targets (sorted and unique)
    """
    r0 = (
        fetch_all_from_githubs_open_green_software_directory()
        + fetch_all_from_awesome_green_software()
        + fetch_all_from_awesome_lwm()
        + fetch_all_from_awesome_sentinel()
    )
    r0.ensure_sorted_and_unique_elements()
    return r0


def fetch_all_from_githubs_open_green_software_directory() -> ParsingTargets:
    # TAG : tools to green software
    readme_str = github_data_io.fetch_repository_readme(
        "https://github.com/github/GreenSoftwareDirectory"
    )
    return __fetch_from_markdown_str(readme_str)


def fetch_all_from_awesome_green_software() -> ParsingTargets:
    # TAG : tools to green software
    readme_str = github_data_io.fetch_repository_readme(
        "https://github.com/Green-Software-Foundation/awesome-green-software"
    )
    return __fetch_from_markdown_str(readme_str)


def fetch_all_from_awesome_lwm() -> ParsingTargets:
    # TAG : large weather models
    readme_str = github_data_io.fetch_repository_readme(
        "https://github.com/jaychempan/Awesome-LWMs"
    )
    return __fetch_from_markdown_str(readme_str)


def fetch_all_from_awesome_sentinel() -> ParsingTargets:
    # TAG : satellite data
    readme_str = github_data_io.fetch_repository_readme(
        "https://github.com/kr-stn/awesome-sentinel"
    )
    return __fetch_from_markdown_str(readme_str)
