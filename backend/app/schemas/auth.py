import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class GitHubAuthCode(BaseModel):
    code: str
    state: str | None = None


class GitHubOAuthUrlResponse(BaseModel):
    url: str
    state: str


class UserAuthResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str | None = None
    avatar_url: str | None = None
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionResponse(BaseModel):
    id: uuid.UUID
    user_agent: str | None = None
    ip_address: str | None = None
    expires_at: datetime
    is_revoked: bool

    model_config = ConfigDict(from_attributes=True)
