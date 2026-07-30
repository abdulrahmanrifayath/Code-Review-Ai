import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class GitHubBranchResponse(BaseModel):
    name: str
    commit_sha: str
    protected: bool = False


class GitHubCommitResponse(BaseModel):
    id: Optional[uuid.UUID] = None
    commit_sha: str
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    message: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GitHubFileResponse(BaseModel):
    filename: str
    status: str
    additions: int
    deletions: int
    patch: Optional[str] = None


class GitHubPRResponse(BaseModel):
    id: uuid.UUID
    repository_id: uuid.UUID
    pr_number: int
    title: str
    body: Optional[str] = None
    state: str
    head_branch: str
    base_branch: str
    head_sha: str
    author_login: str
    html_url: Optional[str] = None
    additions: int
    deletions: int
    changed_files_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GitHubRepoResponse(BaseModel):
    id: uuid.UUID
    name: str
    full_name: str
    owner_login: str
    default_branch: str
    is_private: bool
    language: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncStatusResponse(BaseModel):
    status: str
    message: str
    count: int
