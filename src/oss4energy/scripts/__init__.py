"""
Module containing methods to be run in scripts
"""

import os

import pandas as pd
from tomlkit import document, dump

from oss4energy.src.helpers import sorted_list_of_unique_elements
from oss4energy.src.log import log_info, log_warning
from oss4energy.src.nlp.markdown_io import markdown_to_clean_plaintext
from oss4energy.src.parsers import (
    ParsingTargets,
    ResourceListing,
    github_data_io,
    gitlab_data_io,
    identify_parsing_targets,
    listings,
)
from oss4energy.src.parsers.lfenergy import (
    fetch_all_project_urls_from_lfe_webpage,
    fetch_project_github_urls_from_lfe_energy_project_webpage,
    get_open_source_energy_projects_from_landscape,
)
from oss4energy.src.parsers.opensustain_tech import (
    fetch_all_project_urls_from_opensustain_webpage,
    fetch_listing_of_listings_from_opensustain_webpage,
)

FILE_INPUT_INDEX = "repo_index.toml"
FILE_INPUT_LISTINGS_INDEX = "listings_index.toml"
FILE_OUTPUT_DIR = ".data"
FILE_OUTPUT_LISTING_CSV = f"{FILE_OUTPUT_DIR}/listing_data.csv"
FILE_OUTPUT_LISTING_FEATHER = f"{FILE_OUTPUT_DIR}/listing_data.feather"
FILE_OUTPUT_SUMMARY_TOML = f"{FILE_OUTPUT_DIR}/summary.toml"


def _format_individual_file(file_path: str) -> None:
    os.system(f"black {file_path}")


def format_files():
    _format_individual_file(FILE_INPUT_INDEX)
    _format_individual_file(FILE_INPUT_LISTINGS_INDEX)
    _format_individual_file(FILE_OUTPUT_SUMMARY_TOML)


def _add_projects_to_listing_file(
    parsing_targets: ParsingTargets,
    file_path: str = FILE_INPUT_INDEX,
) -> None:
    log_info(f"Adding projects to {file_path}")
    existing_targets = ParsingTargets.from_toml(file_path)
    new_targets = existing_targets + parsing_targets

    # Cleaning Github repositories links
    new_targets.github_repositories = [
        github_data_io.clean_github_repository_url(i)
        for i in new_targets.github_repositories
    ]

    # Ensuring uniqueness in new targets
    new_targets.ensure_sorted_and_unique_elements()

    # Outputting to a new TOML
    log_info(f"Exporting new index to {file_path}")
    new_targets.to_toml(file_path)

    # Format the file for human readability
    _format_individual_file(file_path)


def discover_projects(
    file_path: str = FILE_INPUT_INDEX,
    listings_file_path: str = FILE_INPUT_LISTINGS_INDEX,
):
    log_info("Indexing LF Energy projects")

    # From webpage
    new_targets = ParsingTargets()
    dropped_urls = []
    rs0 = fetch_all_project_urls_from_lfe_webpage()
    for r in rs0:
        new_targets += fetch_project_github_urls_from_lfe_energy_project_webpage(r)

    # From landscape
    new_targets += get_open_source_energy_projects_from_landscape()

    # Adding from OpenSustainTech
    new_targets += fetch_all_project_urls_from_opensustain_webpage()

    # From different listings
    new_targets += listings.fetch_all(listings_file_path)

    [log_info(f"DROPPING {i} (target is unclear)") for i in dropped_urls]

    _add_projects_to_listing_file(
        new_targets,
        file_path=file_path,
    )
    log_info("Done!")


def add_projects_to_listing(
    project_urls: list[str],
    file_path: str = FILE_INPUT_INDEX,
) -> None:
    """Adds projects from a list into the index file

    :param project_urls: list of URLs to be added
    :param file_path: TOML file link to be updated, defaults to FILE_INPUT_INDEX
    """
    # Splitting URLs into targets
    new_targets = identify_parsing_targets(project_urls)

    _add_projects_to_listing_file(
        new_targets,
        file_path=file_path,
    )
    log_info("Done!")


def generate_listing(target_output_file: str = FILE_OUTPUT_LISTING_CSV) -> None:
    """
    Script to run fetching of the data from the repositories

    Warning: unauthenticated users have a rate limit of 60 calls per hour
    (source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)


    :param target_output_file: name of file to output results to, defaults to FILE_OUTPUT_LISTING_CSV
    :raises ValueError: if output file type is not supported (CSV, JSON)
    :return: /
    """

    log_info("Loading organisations and repositories to be indexed")
    targets = ParsingTargets.from_toml(FILE_INPUT_INDEX)
    targets.ensure_sorted_and_unique_elements()

    bad_organisations = []
    bad_repositories = []

    log_info("Fetching data for all organisations in Github")
    for org_url in targets.github_organisations:
        url2check = org_url.replace("https://", "")
        if url2check.endswith("/"):
            url2check = url2check[:-1]
        if url2check.count("/") > 1:
            log_info(f"SKIPPING repo {org_url}")
            targets.github_repositories.append(org_url)  # Mapping it to repos instead
            continue  # Skip

        try:
            x = github_data_io.fetch_repositories_in_organisation(org_url)
            [targets.github_repositories.append(i) for i in x.values()]
        except Exception as e:
            log_warning(f" > Error with organisation ({e})")
            bad_organisations.append(org_url)

    log_info("Fetching data for all groups in Gitlab")
    for org_url in targets.gitlab_groups:
        url2check = org_url.replace("https://", "")
        if url2check.endswith("/"):
            url2check = url2check[:-1]
        if url2check.count("/") > 1:
            log_info(f"SKIPPING repo {org_url}")
            targets.gitlab_repositories.append(org_url)  # Mapping it to repos instead
            continue  # Skip

        try:
            x = gitlab_data_io.fetch_repositories_in_group(org_url)
            [targets.gitlab_repositories.append(i) for i in x.values()]
        except Exception as e:
            log_warning(f" > Error with organisation ({e})")
            bad_organisations.append(org_url)

    targets.ensure_sorted_and_unique_elements()  # since elements were added
    screening_results = []

    log_info("Fetching data for all repositories in Gitlab")
    for i in targets.gitlab_repositories:
        try:
            screening_results.append(gitlab_data_io.fetch_repository_details(i))
        except Exception as e:
            log_warning(f" > Error with repo ({e})")
            bad_repositories.append(i)

    log_info("Fetching data for all repositories in Github")
    for i in targets.github_repositories:
        try:
            if i.endswith("/.github"):
                continue
            screening_results.append(github_data_io.fetch_repository_details(i))
        except Exception as e:
            log_warning(f" > Error with repo ({e})")
            bad_repositories.append(i)

    df = pd.DataFrame([i.__dict__ for i in screening_results])
    df.set_index("id", inplace=True)

    log_info("Fetching READMEs for all repositories in Github")

    df2export = df.drop(columns=["raw_details"])
    if target_output_file.endswith(".csv"):
        df2export_csv = df.copy()
        df2export_csv["readme"] = df2export_csv["readme"].apply(
            markdown_to_clean_plaintext
        )
        df2export_csv.to_csv(target_output_file, sep=";")
    elif target_output_file.endswith(".json"):
        df2export.T.to_json(target_output_file)
    else:
        raise ValueError(f"Unsupported file type for export: {target_output_file}")

    # Exporting the file to HDF too (faster processing)
    binary_target_output_file = target_output_file
    for i in ["csv", "json"]:
        binary_target_output_file = binary_target_output_file.replace(
            f".{i}", ".feather"
        )
    df2export.reset_index().to_feather(binary_target_output_file)

    print(
        f"""
        
    >>> Data was exported to: {target_output_file}
        
    """
    )

    # Outputting details to a new TOML
    languages = sorted_list_of_unique_elements(df["language"])
    organisations = sorted_list_of_unique_elements(df["organisation"])
    licences = sorted_list_of_unique_elements(df["license"])

    stats = {
        "repositories": len(df),
        "organisations": len(organisations),
    }

    failed = dict(organisations=bad_organisations, repositories=bad_repositories)

    # TOML formatting
    doc = document()
    doc.add("statistics", stats)
    doc.add("failures", failed)
    doc.add("organisations", [str(i) for i in organisations])
    doc.add("language", [str(i) for i in languages])
    doc.add("licences", [str(i) for i in licences])
    log_info(f"Exporting new index to {FILE_OUTPUT_SUMMARY_TOML}")
    with open(FILE_OUTPUT_SUMMARY_TOML, "w") as fp:
        dump(doc, fp, sort_keys=True)

    print(
        f"""
        
    >>> Types were exported to: {FILE_OUTPUT_SUMMARY_TOML}
        
    """
    )
    format_files()


def update_listing_of_listings(
    target_output_file: str = FILE_INPUT_LISTINGS_INDEX,
) -> None:
    list_of_listings = ResourceListing.from_toml(FILE_INPUT_LISTINGS_INDEX)

    # Add data from listings of listings
    listings_open_sustain = fetch_listing_of_listings_from_opensustain_webpage()

    list_of_listings += listings_open_sustain
    list_of_listings.ensure_sorted_and_unique_elements()
    list_of_listings.to_toml(target_output_file)
