"""
Module containing the models and enums for the mapping
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ProjectDetails(BaseModel):
    id: str
    name: str
    organisation: Optional[str]
    url: str
    website: Optional[str]
    description: Optional[str]
    license: Optional[str]
    latest_update: datetime
    language: Optional[str]
    last_commit: Optional[date]
    open_pull_requests: Optional[int]
    raw_details: Optional[dict]
    master_branch: Optional[str]
    readme: Optional[str]
    is_fork: Optional[bool]
