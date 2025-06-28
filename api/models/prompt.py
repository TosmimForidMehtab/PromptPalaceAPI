from typing import List
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime


class Prompt(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    title: str
    description: str
    prompt_text: str
    tags: List[str] = Field(sa_column_kwargs={"nullable": False}, sa_type=JSON)
    media_urls: List[str] = Field(
        default_factory=list, sa_column_kwargs={"nullable": False}, sa_type=JSON
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Vote(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    prompt_id: int
    is_upvote: bool
