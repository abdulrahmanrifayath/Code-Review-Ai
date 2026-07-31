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
from app.schemas.doc_generator_dto import (
    DocGenerationRequest,
    DocGeneratorResponse,
    GeneratedDocItem,
)
from app.services.doc_generator.service import DocGeneratorService

router = APIRouter()


@router.post("/generate", response_model=DocGeneratorResponse)
async def generate_documentation(
    request: DocGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate AI documentation for Docstrings, JavaDocs, README updates, API documentation,
    Missing inline comments, Function descriptions, or Usage examples.
    Saves generated documentation in PostgreSQL database.
    """
    service = DocGeneratorService(db)
    return await service.generate_and_save_doc(request)


@router.get("/repos/{owner}/{repo}/pulls/{number}", response_model=List[GeneratedDocItem])
async def get_pr_generated_docs(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch stored generated documentation records for a Pull Request.
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

    service = DocGeneratorService(db)
    return await service.get_pr_generated_docs(pr.id)


@router.get("/download/{doc_id}")
async def download_generated_doc_file(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Download generated documentation file formatted with attachment headers.
    """
    service = DocGeneratorService(db)
    record = await service.get_doc_by_id(doc_id)

    ext = ".md"
    if record.doc_type in ("javadoc", "java"):
        ext = ".java"
    elif record.doc_type in ("docstring", "python"):
        ext = ".py"

    filename = f"DOC_{record.doc_type.upper()}_{record.target_file}{ext}"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/plain; charset=utf-8",
    }
    return Response(content=record.content, headers=headers, media_type="text/plain")
