"""
Module to manage markdown text
"""

import re


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


def markdown_to_clean_plaintext(x: str) -> str:
    out = _replace_markdown_links(x)
    out = _fix_titles_and_multiple_spaces(out)
    return out
