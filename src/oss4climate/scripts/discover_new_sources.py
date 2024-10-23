"""
This module contains methods to discover new sources of code
"""

from oss4climate.scripts import FILE_INPUT_INDEX, ParsingTargets, log_info
from oss4climate.src.parsers.github_data_io import extract_repository_organisation


def discover_repositories_in_existing_organisations(output_file: str) -> None:
    log_info("Loading organisations and repositories to be indexed")
    targets = ParsingTargets.from_toml(FILE_INPUT_INDEX)

    # Extract organisation to screen for new repositories
    orgs = [extract_repository_organisation(i) for i in targets.github_repositories]

    extended_targets = ParsingTargets(
        github_organisations=orgs,
    )
    extended_targets.ensure_sorted_and_unique_elements()

    # Exporting to TOML file
    extended_targets.to_toml(output_file)
