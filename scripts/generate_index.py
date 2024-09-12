import tomllib
from tomlkit import document, dump

from oss4energy.helpers import sorted_list_of_unique_elements
from oss4energy.log import log_info
from oss4energy.parsers.github_data_io import (
    GITHUB_URL_BASE,
    extract_organisation_and_repository_as_url_block,
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

file_in = "repo_index.toml"
file_out = "repo_index.toml"

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
    for i in sorted_list_of_unique_elements(existing_github_repos + new_github_repos)
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
