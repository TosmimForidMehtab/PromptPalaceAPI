from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str = Field(nullable=False)
    password_hash: str
    profile_image: Optional[str] = Field(
        default="https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
