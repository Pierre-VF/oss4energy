"""
Module for parsers and web I/O
"""

import requests

from oss4energy.database import load_from_database, save_to_database

WEB_SESSION = requests.Session()


def cached_web_get_json(url: str, headers: dict | None = None) -> dict:
    # Uses the cache to ensure that requests are minimised
    out = load_from_database(url)
    if out is None:
        r = WEB_SESSION.get(
            url=url,
            headers=headers,
        )
        r.raise_for_status()
        out = r.json()
        save_to_database(url, out)
    return out
