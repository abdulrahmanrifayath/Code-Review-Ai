import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError, ValidationError
from app.core.security import decrypt_token
from app.models.pull_request import Commit, PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.schemas.github import (
    GitHubBranchResponse,
    GitHubCommitResponse,
    GitHubPRResponse,
    GitHubRepoResponse,
    SyncStatusResponse,
)
from app.services.github_api import GitHubAPIService
from app.services.github_sync import GitHubSyncService

router = APIRouter()


@router.get("/repos", response_model=List[GitHubRepoResponse])
async def list_user_repositories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch synced GitHub repositories from database."""
    statement = select(Repository).where(Repository.is_active.is_(True)).order_by(Repository.updated_at.desc())
    result = await db.execute(statement)
    repos = list(result.scalars().all())
    return repos


@router.post("/repos/sync", response_model=SyncStatusResponse)
async def sync_user_repositories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger GitHub API synchronization for user's accessible repositories."""
    sync_service = GitHubSyncService(db)
    synced_repos = await sync_service.sync_repositories_for_user(current_user)
    return SyncStatusResponse(
        status="success",
        message="Successfully synchronized repositories from GitHub.",
        count=len(synced_repos),
    )


@router.post("/repos/{repo_id}/sync", response_model=SyncStatusResponse)
async def sync_repository_details(
    repo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger GitHub API synchronization for Pull Requests, Commits, and File Diffs of a single repo."""
    sync_service = GitHubSyncService(db)
    repo, synced_prs = await sync_service.sync_pull_requests_for_repo(current_user, repo_id)
    return SyncStatusResponse(
        status="success",
        message=f"Successfully synchronized pull requests for {repo.full_name}.",
        count=len(synced_prs),
    )


@router.get("/repos/{owner}/{repo}/branches", response_model=List[GitHubBranchResponse])
async def get_repository_branches(
    owner: str,
    repo: str,
    current_user: User = Depends(get_current_user),
):
    """Fetch live branches directly from GitHub REST API."""
    if not current_user.encrypted_github_token:
        raise ValidationError("GitHub account is not connected.")
    plain_token = decrypt_token(current_user.encrypted_github_token)
    api = GitHubAPIService(plain_token)
    
    branches_data = await api.get_repository_branches(owner, repo)
    res = []
    for b in branches_data:
        res.append(
            GitHubBranchResponse(
                name=b["name"],
                commit_sha=b["commit"]["sha"],
                protected=b.get("protected", False),
            )
        )
    return res


@router.get("/repos/{owner}/{repo}/pulls", response_model=List[GitHubPRResponse])
async def list_repository_pull_requests(
    owner: str,
    repo: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch pull requests for a repository from database."""
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    pr_stmt = select(PullRequest).where(PullRequest.repository_id == repository.id).order_by(PullRequest.pr_number.desc())
    pr_res = await db.execute(pr_stmt)
    prs = list(pr_res.scalars().all())
    return prs


@router.get("/repos/{owner}/{repo}/pulls/{number}/commits", response_model=List[GitHubCommitResponse])
async def list_pull_request_commits(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch commits for a specific pull request from database."""
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    pr_stmt = select(PullRequest).where(PullRequest.repository_id == repository.id, PullRequest.pr_number == number)
    pr_res = await db.execute(pr_stmt)
    pr = pr_res.scalars().first()
    if not pr:
        raise NotFoundError("PullRequest", number)

    c_stmt = select(Commit).where(Commit.pull_request_id == pr.id).order_by(Commit.created_at.desc())
    c_res = await db.execute(c_stmt)
    commits = list(c_res.scalars().all())
    return commits
