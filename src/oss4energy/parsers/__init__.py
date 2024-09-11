"""
Module for parsers and web I/O
"""

import requests

from oss4energy.database import load_from_database, save_to_database
from oss4energy.log import log_info

WEB_SESSION = requests.Session()


def cached_web_get_json(url: str, headers: dict | None = None) -> dict:
    # Uses the cache to ensure that requests are minimised
    out = load_from_database(url)
    if out is None:
        log_info(f"Web GET: {url}")
        r = WEB_SESSION.get(
            url=url,
            headers=headers,
        )
        r.raise_for_status()
        out = r.json()
        save_to_database(url, out)
    else:
        log_info(f"Cache-loading: {url}")
    return out
