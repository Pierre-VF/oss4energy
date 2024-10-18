import os
from urllib.request import urlretrieve

from oss4energy.scripts import (
    FILE_OUTPUT_DIR,
    FILE_OUTPUT_LISTING_CSV,
    FILE_OUTPUT_LISTING_FEATHER,
    FILE_OUTPUT_SUMMARY_TOML,
)
from oss4energy.src.nlp.search import SearchResults


def download_data():
    URL_BASE = "https://data.pierrevf.consulting/oss4energy"
    URL_RAW_INDEX = f"{URL_BASE}/summary.toml"
    URL_LISTING_CSV = f"{URL_BASE}/listing_data.csv"
    URL_LISTING_FEATHER = f"{URL_BASE}/listing_data.feather"

    os.makedirs(FILE_OUTPUT_DIR, exist_ok=True)
    for url_i, file_i in [
        (URL_RAW_INDEX, FILE_OUTPUT_SUMMARY_TOML),
        (URL_LISTING_CSV, FILE_OUTPUT_LISTING_CSV),
        (URL_LISTING_FEATHER, FILE_OUTPUT_LISTING_FEATHER),
    ]:
        print(f"Fetching {url_i}")
        urlretrieve(url_i, file_i)
        print(f"-> Downloaded to {file_i}")

    print("Download complete")


def search_in_listing() -> None:
    if not os.path.exists(FILE_OUTPUT_LISTING_FEATHER):
        raise RuntimeError(
            "The dataset is not available locally - make sure to download it prior to running this"
        )

    x = SearchResults(FILE_OUTPUT_LISTING_FEATHER)
    print("Initial number of documents")
    print(x.n_documents)

    msg = """
Refine search with command: "[keyword,active,language,show,exit] value"
>>  """

    while (current_input := input(msg).lower()) != "":
        ci_i = current_input.split(" ")
        action_i = ci_i[0]
        if action_i == "active":
            print("Refining by active in past year")
            x.refine_by_active_in_past_year()
        elif action_i == "keyword":
            kw = ci_i[1]
            print(f"Refine by keyword ({kw})")
            x.refine_by_keyword(keyword=kw)
        elif action_i == "language":
            kw = [i.title() for i in ci_i[1].split(",")]
            print(f"Refine by languages ({kw})")
            x.refine_by_languages(languages=kw)  # , include_none=True)
        elif action_i == "show":
            print(x.documents)
        elif action_i == "exit":
            print("Terminating")
            break
        else:
            print(f"Invalid request ({current_input})")
        print(f"{x.n_documents} repositories found")
