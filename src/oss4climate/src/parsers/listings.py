"""
Module parsing https://github.com/github/GreenSoftwareDirectory
"""

from oss4climate.src.log import log_warning
from oss4climate.src.parsers import (
    ParsingTargets,
    ResourceListing,
    github_data_io,
)
from oss4climate.src.parsers import (
    fetch_all_project_urls_from_html_webpage as __fetch_from_webpage,
)
from oss4climate.src.parsers import (
    fetch_all_project_urls_from_markdown_str as __fetch_from_markdown_str,
)


def fetch_all(listings_toml_file: str) -> ParsingTargets:
    """Convenience call for all the below

    :return: sum of all listings targets (sorted and unique)
    """

    listing = ResourceListing.from_toml(listings_toml_file)

    res = ParsingTargets()
    failed_github_readme_listings = []
    failed_webpage_listings = []
    for i in listing.github_readme_listings:
        try:
            res += __fetch_from_markdown_str(github_data_io.fetch_repository_readme(i))
        except Exception:
            log_warning(f"Failed fetching listing README from {i}")
            failed_github_readme_listings.append(i)
    for i in listing.webpage_html:
        try:
            res += __fetch_from_webpage(i)
        except Exception:
            log_warning(f"Failed fetching listing webpage from {i}")
            failed_webpage_listings.append(i)

    # Marking the invalid listings input for tracing
    res += ParsingTargets(
        unknown=listing.fault_urls,
        invalid=listing.fault_invalid_urls,
    )

    res.ensure_sorted_and_unique_elements()
    return res
