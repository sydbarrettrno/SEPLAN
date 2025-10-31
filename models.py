from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    name: str
    password_hash: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
