"""
Module containing the models and enums for the mapping
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProjectDetails(BaseModel):
    name: str
    url: str
    website: Optional[str]
    description: str
    license: str
    latest_update: datetime
    language: str
    raw_details: Optional[dict]
