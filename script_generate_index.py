import time

import pandas as pd
import tomllib
from tomlkit import document, dump

from oss4energy.log import log_info
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
github_urls_lf_energy = []
rs0 = fetch_all_project_urls()
for r in rs0:
    print(f"Indexing: {r}")
    github_urls_lf_energy += fetch_project_github_urls(r)
    time.sleep(0.5)  # To avoid being blacklisted

repos_from_toml["github_hosted"]["organisations"] = list(
    pd.Series(repos_from_toml["github_hosted"]["organisations"] + github_urls_lf_energy)
    .sort_values()
    .unique()
)

# Outputting to a new TOML
doc = document()
for k, v in repos_from_toml.items():
    doc.add(k, v)

log_info(f"Exporting new index to {file_out}")
with open(file_out, "w") as fp:
    dump(doc, fp, sort_keys=True)


log_info("Done!")
