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

    # For compatibility, all these repo must have data in the README
    github_listings = [
        # tools to green software
        "https://github.com/github/GreenSoftwareDirectory",
        "https://github.com/Green-Software-Foundation/awesome-green-software",
        # large weather models
        "https://github.com/jaychempan/Awesome-LWMs",
        # satellite data
        "https://github.com/kr-stn/awesome-sentinel",
        # coastal data
        "https://github.com/chrisleaman/awesome-coastal",
        # agriculture
        "https://github.com/brycejohnston/awesome-agriculture",
        # cryosphere
        "https://github.com/awesome-cryosphere/cryosphere-links",
        # atmospheric, ocean and climate science
        "https://github.com/pangeo-data/awesome-open-climate-science",
        # -------------------------------------------
        # Other
        # -------------------------------------------
        "https://github.com/ESIPFed/Awesome-Earth-Artificial-Intelligence",
        "https://github.com/Agri-Hub/Callisto-Dataset-Collection",
        "https://github.com/IrishMarineInstitute/awesome-erddap",
    ]

    res = ParsingTargets()
    for i in github_listings:
        res += __fetch_from_markdown_str(github_data_io.fetch_repository_readme(i))
    res.ensure_sorted_and_unique_elements()
    return res
