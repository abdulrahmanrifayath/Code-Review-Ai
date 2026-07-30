from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.repository import Repository
from app.models.user import User
from app.schemas.ai_review_dto import AIReviewResponse
from app.services.ai_review_service import AIReviewService

router = APIRouter()


@router.post("/repos/{owner}/{repo}/pulls/{number}/generate", response_model=AIReviewResponse)
async def generate_ai_review(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate an AI Code Review for a Pull Request.
    Combines Tree-sitter static analysis findings, line-numbered diff patches,
    SOLID principle analysis, and OpenAI GPT-4o JSON mode reasoning.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    review_service = AIReviewService(db)
    return await review_service.generate_ai_review(
        user=current_user, repository_id=repository.id, pr_number=number
    )


@router.get("/repos/{owner}/{repo}/pulls/{number}", response_model=AIReviewResponse)
async def get_latest_ai_review(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the latest AI Review report for a Pull Request from database.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    review_service = AIReviewService(db)
    return await review_service.get_latest_ai_review(
        repository_id=repository.id, pr_number=number
    )
