from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.repository import Repository
from app.models.user import User
from app.schemas.security_dto import SecurityDashboardSummaryResponse
from app.services.security_analysis_service import SecurityAnalysisService

router = APIRouter()


@router.post("/repos/{owner}/{repo}/pulls/{number}/scan", response_model=SecurityDashboardSummaryResponse)
async def scan_pull_request_security(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute SAST Security Analyzer engine scanning for SQL Injection, Hardcoded Passwords,
    API Keys, JWT flaws, Command Injection, Unsafe Files, XSS, CSRF, and Path Traversal.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    security_service = SecurityAnalysisService(db)
    return await security_service.run_security_scan(
        user=current_user, repository_id=repository.id, pr_number=number
    )


@router.get("/repos/{owner}/{repo}/pulls/{number}/dashboard", response_model=SecurityDashboardSummaryResponse)
async def get_security_dashboard(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch stored Security Dashboard summary data (severity metrics, CWE mappings, remediation guides).
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    security_service = SecurityAnalysisService(db)
    return await security_service.get_security_dashboard(
        repository_id=repository.id, pr_number=number
    )
