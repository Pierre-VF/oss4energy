"""
Module parsing https://github.com/github/GreenSoftwareDirectory
"""

from oss4energy.src.parsers import (
    ParsingTargets,
    github_data_io,
)
from oss4energy.src.parsers import (
    fetch_all_project_urls_from_markdown_str as __fetch_from_markdown_str,
)


def fetch_all_project_urls_from_readme() -> ParsingTargets:
    readme_str = github_data_io.fetch_repository_readme(
        "https://github.com/github/GreenSoftwareDirectory"
    )
    return __fetch_from_markdown_str(readme_str)
