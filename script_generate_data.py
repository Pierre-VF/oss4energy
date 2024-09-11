"""
Script to run fetching of the data from the repositories

Warning: unauthenticated users have a rate limit of 60 calls per hour
 (source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)
"""

import pandas as pd
import tomllib

from oss4energy.log import log_info
from oss4energy.parsers.github_data_io import (
    fetch_repositories_in_organisation,
    fetch_repository_details,
)

log_info("Loading organisations and repositories to be indexed")
with open("repo_index.toml", "rb") as f:
    repos_from_toml = tomllib.load(f)


bad_organisations = []
bad_repositories = []


log_info("Fetching data for all organisations in Github")
repos_to_screen = []
for org_url in repos_from_toml["github_hosted"]["organisations"]:
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
for i in repos_to_screen:
    try:
        if i.endswith("/.github"):
            continue
        screening_results.append(fetch_repository_details(i))
    except Exception as e:
        print(f" > Error with repo ({e})")
        bad_repositories.append(i)


df = pd.DataFrame([i.__dict__ for i in screening_results])

df.drop(columns=["raw_details"]).to_csv(".data/export.csv", sep=";")


df_python = df[df["language"].apply(lambda x: x == "Python")]
df_java = df[df["language"].apply(lambda x: x == "Java")]


# Non deprecated
def _f_description_ok(x):
    if x is None:
        return True
    x_lower = x.lower()
    if "deprecated" in x_lower:
        return False
    elif "legacy" in x_lower:
        return False
    else:
        return True


df_non_depr = df[df["description"].apply(_f_description_ok)]

print("DONE!")
