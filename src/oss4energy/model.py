"""
Module containing the models and enums for the mapping
"""

from datetime import datetime
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
    raw_details: Optional[dict]
