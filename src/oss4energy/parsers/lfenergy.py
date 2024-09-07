"""
Parser for LF Energy projects
"""

import requests
from bs4 import BeautifulSoup

_PROJECT_PAGE_URL_BASE = "https://lfenergy.org/projects/"


def fetch_all_project_urls() -> list[str]:
    r = requests.get("https://lfenergy.org/our-projects/")
    r.raise_for_status()
    b = BeautifulSoup(r.text, features="html.parser")

    rs = b.findAll(name="a")
    shortlisted_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith(_PROJECT_PAGE_URL_BASE)
    ]
    # Ensure unicity of links
    return list(set(shortlisted_urls))


def fetch_project_github_urls(project_url: str) -> list[str]:
    if not project_url.startswith(_PROJECT_PAGE_URL_BASE):
        raise ValueError(f"Unsupported page URL ({project_url})")
    r = requests.get(project_url)
    r.raise_for_status()
    b = BeautifulSoup(r.text, features="html.parser")

    rs = b.findAll(name="a", attrs={"class": "projects-icon"})
    github_urls = [
        i for i in [x.get("href") for x in rs] if i.startswith("https://github.com/")
    ]
    return [i for i in github_urls if not i.endswith(".md")]


if __name__ == "__main__":
    import time

    rs0 = fetch_all_project_urls()
    github_urls = []
    for r in rs0:
        print(r)
        github_urls += fetch_project_github_urls(r)
        time.sleep(0.5)  # To avoid being blacklisted

    # Outputting TOML
    from tomlkit import comment, document, dump, nl, table

    doc = document()
    doc.add(comment("Indexing of all LF Energy projects"))
    doc.add(nl())
    doc.add("title", "LF Energy projects")

    lfe = table()
    lfe.add("organisations", github_urls)

    # Adding the table to the document
    doc.add("lfe", lfe)

    with open("lfe_projects.toml", "w") as fp:
        dump(doc, fp, sort_keys=True)

    print("Done!")
