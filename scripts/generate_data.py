"""
Script to run fetching of the data from the repositories

Warning: unauthenticated users have a rate limit of 60 calls per hour
 (source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)
"""

import pandas as pd
import tomllib
from tomlkit import document, dump

from oss4energy.helpers import sorted_list_of_unique_elements
from oss4energy.log import log_info
from oss4energy.parsers.github_data_io import (
    fetch_repositories_in_organisation,
    fetch_repository_details,
    fetch_repository_readme,
)

target_output_file = ".data/export.json"

log_info("Loading organisations and repositories to be indexed")
with open("repo_index.toml", "rb") as f:
    repos_from_toml = tomllib.load(f)


bad_organisations = []
bad_repositories = []


log_info("Fetching data for all organisations in Github")
repos_to_screen = []
for org_url in sorted_list_of_unique_elements(
    repos_from_toml["github_hosted"]["organisations"]
):
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


df["readme"] = df["url"].apply(fetch_repository_readme)


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
output_types = ".data/all_types.toml"  # This is to be coordinated with the makefile

languages = sorted_list_of_unique_elements(df["language"])
organisations = sorted_list_of_unique_elements(df["organisation"])
licences = sorted_list_of_unique_elements(df["license"])

# TOML formatting
doc = document()
doc.add("organisations", [str(i) for i in organisations])
doc.add("language", [str(i) for i in languages])
doc.add("licences", [str(i) for i in licences])
log_info(f"Exporting new index to {output_types}")
with open(output_types, "w") as fp:
    dump(doc, fp, sort_keys=True)

print(
    f"""
    
>>> Types were exported to: {output_types}
    
"""
)
