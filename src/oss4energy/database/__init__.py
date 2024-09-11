"""
Module to manage a database input
"""

import json
from datetime import UTC, datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select

from oss4energy.config import SETTINGS


# -------------------------------------------------------------------------------------
# Models
# -------------------------------------------------------------------------------------
class Cache(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True, nullable=False)
    value: str
    fetched_at: datetime


# -------------------------------------------------------------------------------------
# Engine
# -------------------------------------------------------------------------------------
_ENGINE = create_engine(
    f"sqlite:///{SETTINGS.SQLITE_DB}",
    echo=False,
)
SQLModel.metadata.create_all(_ENGINE)


# -------------------------------------------------------------------------------------
# Actual methods
# -------------------------------------------------------------------------------------
def load_from_database(key: str, is_json: bool) -> dict | None:
    with Session(_ENGINE) as session:
        res = session.exec(select(Cache).where(Cache.id == key)).first()
    if res is None:
        return None
    else:
        if is_json:
            return json.loads(res.value)
        else:
            return res.value


def save_to_database(key: str, value: dict, is_json: bool) -> None:
    if is_json:
        value_to_write = json.dumps(value)
    else:
        value_to_write = value

    with Session(_ENGINE) as session:
        session.add(
            Cache(id=key, value=value_to_write, fetched_at=datetime.now(tz=UTC))
        )
        session.commit()
