"""
Module to manage markdown text
"""

import re

from bs4 import BeautifulSoup
from markdown import markdown


def _replace_markdown_links(text):
    # Regex pattern to match markdown links
    pattern = r"\[([^\]]+)\]\(.*?\)"

    # Replacement function to keep only the link text
    def repl(match):
        return match.group(1)

    # Use the sub method to replace the links
    result = re.sub(pattern, repl, text)

    return result


def _fix_titles_and_multiple_spaces(text: str) -> str:
    # Use the sub method to replace the links
    result = text.replace("#", " ")
    result = re.sub(r"\s+", " ", result)
    return result


def markdown_to_clean_plaintext(x: str | None) -> str | None:
    """This method converts a markdown string to plaintext

    :param x: _description_
    :return: _description_
    """
    if x is None:
        return None
    html = markdown(x)
    x = BeautifulSoup(html)

    full_content = ""
    for i in ["p", "h1", "h2", "h3"]:
        for j in x.find_all(i):
            full_content = full_content + " " + j.get_text(" ", strip=True)
    # print(full_content)

    # out = _replace_markdown_links(x)
    # out = _fix_titles_and_multiple_spaces(out)
    return full_content.strip()
