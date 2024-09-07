"""
Script to run fetching of the data from the repositories

Warning: unauthenticated users have a rate limit of 60 calls per hour
 (source: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28)
"""

import time

import pandas as pd
import tomllib

from oss4energy.github_data_io import (
    fetch_repositories_in_organisation,
    fetch_repository_details,
)

with open("repo_index.toml", "rb") as f:
    repos_from_toml = tomllib.load(f)


repos_to_screen = []
for org_url in repos_from_toml["github_hosted"]["organisations"]:
    x = fetch_repositories_in_organisation(org_url)
    [repos_to_screen.append(i) for i in x.values()]
    time.sleep(0.5)  # To avoid triggering rate limits on API

screening_results = []
for i in repos_to_screen:
    try:
        if i.endswith("/.github"):
            continue
        print(i)
        screening_results.append(fetch_repository_details(i))
        time.sleep(0.5)  # To avoid triggering rate limits on API
    except Exception as e:
        print(f" > Error ({e})")


df = pd.DataFrame([i.__dict__ for i in screening_results])

df.to_csv("export.csv", sep=";")


print(repos_from_toml)
