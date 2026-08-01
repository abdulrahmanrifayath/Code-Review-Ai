from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.repository import Repository
from app.models.user import User
from app.schemas.parser import ParsedPRSummaryResponse
from app.services.pr_parser_service import PullRequestParserService

router = APIRouter()


@router.post("/repos/{owner}/{repo}/pulls/{number}/parse", response_model=ParsedPRSummaryResponse)
async def parse_pull_request_diffs(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Download PR diff patches from GitHub API, parse unified diff hunks,
    extract line numbers and added/deleted lines, detect programming languages,
    and persist results in database.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    parser_service = PullRequestParserService(db)
    return await parser_service.parse_and_store_pull_request_diffs(
        user=current_user, repository_id=repository.id, pr_number=number
    )


@router.get("/repos/{owner}/{repo}/pulls/{number}/diffs", response_model=ParsedPRSummaryResponse)
async def get_stored_pull_request_diffs(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve stored parsed diffs, added/deleted line mappings, and language stats for a PR.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    parser_service = PullRequestParserService(db)
    return await parser_service.get_stored_pull_request_diffs(
        repository_id=repository.id, pr_number=number
    )
