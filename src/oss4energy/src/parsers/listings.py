"""
Module parsing https://github.com/github/GreenSoftwareDirectory
"""

from oss4energy.src.parsers import (
    ParsingTargets,
    ResourceListing,
    github_data_io,
)
from oss4energy.src.parsers import (
    fetch_all_project_urls_from_markdown_str as __fetch_from_markdown_str,
)


def fetch_all(listings_toml_file: str) -> ParsingTargets:
    """Convenience call for all the below

    :return: sum of all listings targets (sorted and unique)
    """

    listing = ResourceListing.from_toml(listings_toml_file)

    res = ParsingTargets()
    for i in listing.github_readme_listings:
        res += __fetch_from_markdown_str(github_data_io.fetch_repository_readme(i))
    res.ensure_sorted_and_unique_elements()
    return res
