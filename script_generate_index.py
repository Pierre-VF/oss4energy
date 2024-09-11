import time

import pandas as pd
import tomllib
from tomlkit import document, dump

from oss4energy.log import log_info
from oss4energy.parsers.github_data_io import GithubTargetType
from oss4energy.parsers.lfenergy import (
    fetch_all_project_urls,
    fetch_project_github_urls,
)

file_in = "repo_index.toml"
file_out = "repo_index.toml"

log_info(f"Loading existing index from {file_in}")
with open(file_in, "rb") as f:
    repos_from_toml = tomllib.load(f)

log_info("Indexing LF Energy projects")
github_organisations_urls_lf_energy = []
github_repositories_urls_lf_energy = []
unknowns_lf_energy = []
rs0 = fetch_all_project_urls()
for r in rs0:
    print(f"Indexing: {r}")
    orgs_r, repos_r, unknown_r = fetch_project_github_urls(r)
    github_organisations_urls_lf_energy += orgs_r
    github_repositories_urls_lf_energy += repos_r
    unknowns_lf_energy += unknown_r
    time.sleep(0.5)  # To avoid being blacklisted


# Checking
existing_github_orgs = repos_from_toml["github_hosted"]["organisations"]
existing_github_repos = repos_from_toml["github_hosted"]["repositories"]
new_github_orgs = []
dropped_urls = []
for i in existing_github_orgs:
    tt_i = GithubTargetType.identify(i)
    if tt_i is GithubTargetType.ORGANISATION:
        new_github_orgs.append(i)
    elif tt_i is GithubTargetType.REPOSITORY:
        existing_github_repos.append(i)
    else:
        dropped_urls.append(i)
        log_info("DROPPING {i} (target is unclear)")

# Adding new
repos_from_toml["github_hosted"]["organisations"] = list(
    pd.Series(new_github_orgs + github_organisations_urls_lf_energy)
    .sort_values()
    .unique()
)
repos_from_toml["github_hosted"]["repositories"] = list(
    pd.Series(existing_github_repos + github_repositories_urls_lf_energy)
    .sort_values()
    .unique()
)

repos_from_toml["dropped_targets"]["urls"] = dropped_urls

# Outputting to a new TOML
doc = document()
for k, v in repos_from_toml.items():
    doc.add(k, v)

log_info(f"Exporting new index to {file_out}")
with open(file_out, "w") as fp:
    dump(doc, fp, sort_keys=True)


log_info("Done!")
