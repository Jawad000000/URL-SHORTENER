from datetime import datetime
from pydantic import BaseModel, HttpUrl


# -------------------------
# Request Schemas
# -------------------------

class ShortURLRequest(BaseModel):
    url: HttpUrl


# -------------------------
# Base Response Schema
# -------------------------

class ShortURLResponse(BaseModel):
    url: HttpUrl
    short_url: HttpUrl
    short_code: str
    created_at: datetime
    updated_at: datetime


# -------------------------
# Stats Response Schema
# -------------------------

class URLStatsResponse(ShortURLResponse):
    access_count: int
