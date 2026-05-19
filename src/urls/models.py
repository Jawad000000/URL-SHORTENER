from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column, func
import sqlalchemy.dialects.postgresql as pg

# if TYPE_CHECKING:
#     from src.auth.models import User


class Url(SQLModel, table=True):
    __tablename__ = "urls"

    id: Optional[int] = Field(default=None, primary_key=True)

    original_url: str = Field(nullable=False)

    short_code: str = Field(
        nullable=False,
        unique=True,
        index=True
    )

    access_count: int = Field(default=0)

    user_id: int = Field(
        foreign_key="users.id",
        index=True
    )

    # user: Optional["User"] = Relationship(
    #     back_populates="urls"
    # )

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            server_default=func.now()
        )
    )

    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            server_default=func.now(),
            onupdate=func.now(),
        )
    )
