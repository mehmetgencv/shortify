from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class URLBase(BaseModel):
    url: HttpUrl

class URLCreate(URLBase):
    pass

class URL(URLBase):
    id: int
    short_code: str
    original_url: str
    created_at: datetime
    clicks: int

    class Config:
        from_attributes = True

class URLResponse(BaseModel):
    short_url: str
    original_url: str 