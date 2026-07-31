from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.repository import Repository
from app.models.user import User
from app.schemas.quality_dto import (
    PRQualityScoreResponse,
    QualityHistoryResponse,
    RepoQualityScoreResponse,
)
from app.services.code_quality_engine.service import CodeQualityEngineService

router = APIRouter()


@router.get("/repos/{owner}/{repo}/score", response_model=RepoQualityScoreResponse)
async def get_repository_quality_score(
    owner: str,
    repo: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch Code Quality Engine metrics for a repository (Maintainability, Technical Debt hours,
    Complexity, Documentation coverage %, and Architecture score).
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    quality_service = CodeQualityEngineService(db)
    return await quality_service.get_repository_quality_score(repository.id)


@router.post("/repos/{owner}/{repo}/pulls/{number}/calculate", response_model=PRQualityScoreResponse)
async def calculate_pr_quality_score(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute Code Quality Engine calculation for a Pull Request and store snapshot in QualityHistory.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    quality_service = CodeQualityEngineService(db)
    return await quality_service.calculate_pr_quality_score(repository.id, number)


@router.get("/repos/{owner}/{repo}/trends", response_model=QualityHistoryResponse)
async def get_repository_quality_trends(
    owner: str,
    repo: str,
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch historical quality trend timeline over specified days (default 30d).
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    quality_service = CodeQualityEngineService(db)
    return await quality_service.get_repository_trends(repository.id, days=days)
