import uuid
from typing import List
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.schemas.test_generator_dto import (
    GeneratedTestItem,
    TestGenerationRequest,
    TestGeneratorResponse,
)
from app.services.test_generator.service import TestGeneratorService

router = APIRouter()


@router.post("/generate", response_model=TestGeneratorResponse)
async def generate_test_suite(
    request: TestGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI unit/integration test suite across JUnit (Java), pytest (Python),
    or Jest (JavaScript/TypeScript) for Positive, Negative, Boundary, or Mock scenarios.
    Saves generated tests in PostgreSQL database.
    """
    service = TestGeneratorService(db)
    return await service.generate_and_save_test(request)


@router.get("/repos/{owner}/{repo}/pulls/{number}", response_model=List[GeneratedTestItem])
async def get_pr_generated_tests(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch stored generated test records for a Pull Request.
    """
    repo_stmt = select(Repository).where(Repository.full_name == f"{owner}/{repo}")
    repo_res = await db.execute(repo_stmt)
    repository = repo_res.scalars().first()
    if not repository:
        raise NotFoundError("Repository", f"{owner}/{repo}")

    pr_stmt = select(PullRequest).where(
        PullRequest.repository_id == repository.id, PullRequest.pr_number == number
    )
    pr_res = await db.execute(pr_stmt)
    pr = pr_res.scalars().first()
    if not pr:
        raise NotFoundError("PullRequest", number)

    service = TestGeneratorService(db)
    return await service.get_pr_generated_tests(pr.id)


@router.get("/download/{test_id}")
async def download_generated_test_file(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Download generated test file formatted with attachment headers.
    """
    service = TestGeneratorService(db)
    record = await service.get_test_by_id(test_id)

    filename = record.test_name or f"test_{record.id}.py"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/plain; charset=utf-8",
    }
    return Response(content=record.generated_code, headers=headers, media_type="text/plain")
