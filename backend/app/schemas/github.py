import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GitHubBranchResponse(BaseModel):
    name: str
    commit_sha: str
    protected: bool = False


class GitHubCommitResponse(BaseModel):
    id: uuid.UUID | None = None
    commit_sha: str
    author_name: str | None = None
    author_email: str | None = None
    message: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GitHubFileResponse(BaseModel):
    filename: str
    status: str
    additions: int
    deletions: int
    patch: str | None = None


class GitHubPRResponse(BaseModel):
    id: uuid.UUID
    repository_id: uuid.UUID
    pr_number: int
    title: str
    body: str | None = None
    state: str
    head_branch: str
    base_branch: str
    head_sha: str
    author_login: str
    html_url: str | None = None
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
    language: str | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncStatusResponse(BaseModel):
    status: str
    message: str
    count: int
