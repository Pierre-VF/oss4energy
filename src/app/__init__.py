"""
FastAPI app to operate a search
"""

import pathlib
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tqdm import tqdm
from uvicorn import run

from oss4energy.scripts import (
    FILE_OUTPUT_LISTING_FEATHER,
)
from oss4energy.src.nlp.search import SearchResults
from oss4energy.src.nlp.search_engine import SearchEngine

script_dir = pathlib.Path(__file__).resolve().parent
templates_path = script_dir / "templates"
static_path = script_dir / "static"
SEARCH_ENGINE_DESCRIPTIONS = SearchEngine()
SEARCH_ENGINE_READMES = SearchEngine()
DOCUMENTS = SearchResults("../../" + FILE_OUTPUT_LISTING_FEATHER).documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    for __, r in tqdm(DOCUMENTS.iterrows()):
        # Skip repos with missing info
        for k in ["readme", "description"]:
            if r[k] is None:
                r[k] = ""
        SEARCH_ENGINE_DESCRIPTIONS.index(url=r["url"], content=r["description"])
        SEARCH_ENGINE_READMES.index(r["url"], content=r["readme"])
    yield
    print("Quitting app")


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


def get_top_urls(scores_dict: dict, n: int):
    sorted_urls = sorted(scores_dict.items(), key=lambda x: x[1], reverse=True)
    top_n_urls = sorted_urls[:n]
    top_n_dict = dict(top_n_urls)
    return top_n_dict


@app.get("/", response_class=HTMLResponse)
async def search(request: Request):
    posts = SEARCH_ENGINE_DESCRIPTIONS.posts
    return templates.TemplateResponse(
        "search.html", {"request": request, "posts": posts}
    )


@app.get("/results", response_class=HTMLResponse)
async def search_results(request: Request, query: str, language: Optional[str] = None):
    res_desc = SEARCH_ENGINE_DESCRIPTIONS.search(query)
    res_readme = SEARCH_ENGINE_DESCRIPTIONS.search(query)

    df_combined = (
        res_desc.to_frame("description")
        .merge(
            res_readme.to_frame("readme"),
            how="outer",
            left_index=True,
            right_index=True,
        )
        .fillna(0)
    )
    df_combined["score"] = df_combined["description"] * 10 + df_combined["readme"]

    # Adding a primitive refinment mechanism by language (not implemented in the most effective manner)
    if language:
        local_docs = DOCUMENTS[DOCUMENTS["language"] == language].drop(
            columns=["readme"]
        )
    else:
        local_docs = DOCUMENTS.drop(columns=["readme"])

    df_out = local_docs.merge(
        df_combined[["score"]].sort_values(by="score", ascending=False),
        how="inner",
        left_on="url",
        right_index=True,
    )
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "results": df_out.head(100),  # TODO: for speed make this earlier on
            "query": query,
        },
    )


@app.get("/about")
def read_about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


if __name__ == "__main__":
    run(app, host="127.0.0.1", port=8000)
