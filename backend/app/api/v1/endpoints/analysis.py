from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.repository import Repository
from app.models.user import User
from app.schemas.analysis_dto import AnalysisSummaryResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.post("/repos/{owner}/{repo}/pulls/{number}/analyze", response_model=AnalysisSummaryResponse)
async def analyze_pull_request(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute multi-tool static code analysis engine (Tree-sitter AST complexity,
    Pylint, Flake8, Bandit, ESLint, Checkstyle, PMD) across PR changed files.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    analysis_service = AnalysisService(db)
    return await analysis_service.run_static_analysis(
        user=current_user, repository_id=repository.id, pr_number=number
    )


@router.get("/repos/{owner}/{repo}/pulls/{number}/findings", response_model=AnalysisSummaryResponse)
async def get_pull_request_findings(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve stored static analysis findings (Security, Performance, Code Smells) for a PR.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    analysis_service = AnalysisService(db)
    return await analysis_service.get_pr_findings(
        repository_id=repository.id, pr_number=number
    )
