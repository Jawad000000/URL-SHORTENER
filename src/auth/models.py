from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column, func
import sqlalchemy.dialects.postgresql as pg

# if TYPE_CHECKING:
#     from src.urls.models import Url


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)

    username: str
    email: str
    password_hash: str

    is_verified: bool = False

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP, server_default=func.now())
    )

    # urls: list["Url"] = Relationship(back_populates="user")
