"""
Module to manage a database input
"""

import json

from sqlmodel import Field, Session, SQLModel, create_engine, select

from oss4energy.config import SETTINGS


# -------------------------------------------------------------------------------------
# Models
# -------------------------------------------------------------------------------------
class Cache(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True, nullable=False)
    value: str


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
def load_from_database(key: str) -> dict | None:
    with Session(_ENGINE) as session:
        res = session.exec(select(Cache).where(Cache.id == key)).first()
    if res is None:
        return None
    else:
        return json.loads(res.value)


def save_to_database(key: str, value: dict) -> None:
    jsoned_value = json.dumps(value)

    with Session(_ENGINE) as session:
        session.add(Cache(id=key, value=jsoned_value))
        session.commit()
