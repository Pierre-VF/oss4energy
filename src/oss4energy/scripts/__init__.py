"""
Module containing methods to be run in scripts
"""

import os
from ftplib import FTP

import pandas as pd
import tomllib
from tomlkit import document, dump

from oss4energy.config import SETTINGS
from oss4energy.helpers import sorted_list_of_unique_elements
from oss4energy.log import log_info
from oss4energy.parsers.github_data_io import (
    GITHUB_URL_BASE,
    extract_organisation_and_repository_as_url_block,
    fetch_repositories_in_organisation,
    fetch_repository_details,
    fetch_repository_readme,
    split_organisations_repositories_others,
)
from oss4energy.parsers.lfenergy import (
    fetch_all_project_urls_from_lfe_webpage,
    fetch_project_github_urls_from_lfe_energy_project_webpage,
    get_open_source_energy_projects_from_landscape,
)
from oss4energy.parsers.opensustain_tech import (
    fetch_all_project_urls_from_opensustain_webpage,
)

FILE_INPUT_INDEX = "repo_index.toml"
FILE_OUTPUT_LISTING_CSV = ".data/listing_data.csv"
FILE_OUTPUT_SUMMARY_TOML = ".data/summary.toml"


def format_files():
    os.system(f"black {FILE_INPUT_INDEX}")
    os.system(f"black {FILE_OUTPUT_SUMMARY_TOML}")


def discover_projects():
    file_in = FILE_INPUT_INDEX
    file_out = FILE_INPUT_INDEX

    log_info(f"Loading existing index from {file_in}")
    with open(file_in, "rb") as f:
        repos_from_toml = tomllib.load(f)

    existing_github_orgs = repos_from_toml["github_hosted"]["organisations"]
    existing_github_repos = repos_from_toml["github_hosted"]["repositories"]

    log_info("Indexing LF Energy projects")

    # From webpage
    new_github_orgs = []
    new_github_repos = []
    dropped_urls = []
    rs0 = fetch_all_project_urls_from_lfe_webpage()
    for r in rs0:
        orgs_r, repos_r, unknown_r = (
            fetch_project_github_urls_from_lfe_energy_project_webpage(r)
        )
        new_github_orgs += orgs_r
        new_github_repos += repos_r
        dropped_urls += unknown_r

    # From landscape
    orgs_r, repos_r, unknown_r = get_open_source_energy_projects_from_landscape()
    new_github_orgs += orgs_r
    new_github_repos += repos_r
    dropped_urls += unknown_r

    # Checking
    new_github_orgs, new_github_repos, dropped_urls
    orgs_r, repos_r, unknown_r = split_organisations_repositories_others(
        existing_github_orgs
    )
    new_github_orgs += orgs_r
    new_github_repos += repos_r
    dropped_urls += unknown_r  # Dropping non-Github for now

    # Adding from OpenSustainTech
    (
        github_orgs_urls_opensustaintech,
        github_repos_urls_opensustaintech,
        other_urls_opensustaintech,
    ) = fetch_all_project_urls_from_opensustain_webpage()
    new_github_orgs += github_orgs_urls_opensustaintech
    new_github_repos += github_repos_urls_opensustaintech
    dropped_urls += other_urls_opensustaintech

    [log_info(f"DROPPING {i} (target is unclear)") for i in dropped_urls]
    existing_github_repos += new_github_repos

    cleaned_repositories_url = [
        GITHUB_URL_BASE + extract_organisation_and_repository_as_url_block(i)
        for i in sorted_list_of_unique_elements(
            existing_github_repos + new_github_repos
        )
    ]

    # Adding new
    repos_from_toml["github_hosted"]["organisations"] = sorted_list_of_unique_elements(
        existing_github_orgs + new_github_orgs
    )
    repos_from_toml["github_hosted"]["repositories"] = sorted_list_of_unique_elements(
        cleaned_repositories_url
    )
    repos_from_toml["dropped_targets"]["urls"] = sorted_list_of_unique_elements(
        dropped_urls
    )

    # Outputting to a new TOML
    doc = document()
    for k, v in repos_from_toml.items():
        doc.add(k, v)

    log_info(f"Exporting new index to {file_out}")
    with open(file_out, "w") as fp:
        dump(doc, fp, sort_keys=True)

    log_info("Done!")


def generate_listing():
    """
    Script to run fetching of the data from the repositories

    Warning: unauthenticated users have a rate limit of 60 calls per hour
    (source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)
    """

    target_output_file = FILE_OUTPUT_LISTING_CSV

    log_info("Loading organisations and repositories to be indexed")
    with open(FILE_INPUT_INDEX, "rb") as f:
        repos_from_toml = tomllib.load(f)

    bad_organisations = []
    bad_repositories = []

    organisations_to_screen = repos_from_toml["github_hosted"]["organisations"]
    repos_to_screen = repos_from_toml["github_hosted"]["repositories"]

    log_info("Fetching data for all organisations in Github")
    for org_url in sorted_list_of_unique_elements(organisations_to_screen):
        url2check = org_url.replace("https://", "")
        if url2check.endswith("/"):
            url2check = url2check[:-1]
        if url2check.count("/") > 1:
            log_info(f"SKIPPING repo {org_url}")
            continue  # Skip

        try:
            x = fetch_repositories_in_organisation(org_url)
            [repos_to_screen.append(i) for i in x.values()]
        except Exception as e:
            print(f" > Error with organisation ({e})")
            bad_organisations.append(org_url)

    log_info("Fetching data for all repositories in Github")
    screening_results = []
    for i in sorted_list_of_unique_elements(repos_to_screen):
        try:
            if i.endswith("/.github"):
                continue
            screening_results.append(fetch_repository_details(i))
        except Exception as e:
            print(f" > Error with repo ({e})")
            bad_repositories.append(i)

    df = pd.DataFrame([i.__dict__ for i in screening_results])
    df.set_index("id", inplace=True)

    def _f_readme(x):
        y = fetch_repository_readme(x)
        newline_marker = ""
        y = y.replace("\n", newline_marker)
        y = y.replace("\r", newline_marker)
        return y[:1000]

    log_info("Fetching READMEs for all repositories in Github")
    df["readme"] = df["url"].apply(_f_readme)

    if target_output_file.endswith(".csv"):
        df.drop(columns=["raw_details"]).to_csv(target_output_file, sep=";")
    elif target_output_file.endswith(".json"):
        df.drop(columns=["raw_details"]).T.to_json(target_output_file)
    else:
        raise ValueError(f"Unsupported file type for export: {target_output_file}")

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


def publish_to_ftp():
    for i in [
        SETTINGS.EXPORT_FTP_URL,
        SETTINGS.EXPORT_FTP_USER,
        SETTINGS.EXPORT_FTP_PASSWORD,
    ]:
        if i is None:
            raise EnvironmentError(
                f"{i.__name__} must be defined for FTP export to work"
            )
        if len(i) == 0:
            raise EnvironmentError(
                f"{i.__name__} must have an adequate value for FTP export to work"
            )
    files_out = [
        FILE_OUTPUT_SUMMARY_TOML,
        FILE_OUTPUT_LISTING_CSV,
    ]

    with FTP(
        host=SETTINGS.EXPORT_FTP_URL,
        user=SETTINGS.EXPORT_FTP_USER,
        passwd=SETTINGS.EXPORT_FTP_PASSWORD,
    ) as ftp:
        try:
            ftp.mkd("oss4energy")
        except:
            pass
        ftp.cwd("oss4energy")
        for i in files_out:
            with open(i, "rb") as fp:
                log_info(f"Uploading {i}")
                ftp.storbinary("STOR %s" % os.path.basename(i), fp, blocksize=1024)
