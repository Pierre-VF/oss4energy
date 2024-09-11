"""
Script to run fetching of the data from the repositories

Warning: unauthenticated users have a rate limit of 60 calls per hour
 (source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)
"""

import pandas as pd
import tomllib

from oss4energy.parsers.github_data_io import (
    fetch_repositories_in_organisation,
    fetch_repository_details,
)

with open(".data/lfe_projects.toml", "rb") as f:
    repos_from_toml = tomllib.load(f)

r = repos_from_toml["lfe"]["organisations"]

sorted_r = pd.Series(r).sort_values().to_list()

bases = []
for i in sorted_r:
    ok = True
    for j in bases:
        if i.startswith(j):
            ok = False
            print(f" Excluding {j}")
            continue
    if ok:
        bases.append(i)


with open("repo_index.toml", "rb") as f:
    repos_from_toml = tomllib.load(f)


bad_organisations = []
bad_repositories = []

repos_to_screen = []
for org_url in repos_from_toml["github_hosted"]["organisations"]:
    try:
        x = fetch_repositories_in_organisation(org_url)
        [repos_to_screen.append(i) for i in x.values()]
    except Exception as e:
        print(f" > Error with organisation ({e})")
        bad_organisations.append(org_url)

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

df.to_csv(".data/export.csv", sep=";")

print("DONE!")
