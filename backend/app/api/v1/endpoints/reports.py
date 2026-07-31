import json
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.schemas.report_dto import (
    ReportGenerationRequest,
    ReportGeneratorResponse,
    ReviewReportItem,
)
from app.services.reports.report_generator import ProfessionalReportGeneratorEngine
from app.services.reports.service import ReportService

router = APIRouter()


@router.post("/generate", response_model=ReportGeneratorResponse)
async def generate_review_report(
    request: ReportGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate professional review report with Executive Summary, Quality Score, Security Summary,
    Performance Summary, Bug Summary, Code Smells, Generated Tests, and Documentation Suggestions.
    Supports PDF, Markdown, HTML, and JSON export formats.
    """
    service = ReportService(db)
    return await service.generate_and_save_report(request)


@router.get("/{report_id}", response_model=ReviewReportItem)
async def get_review_report_by_id(
    report_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve stored review report by ID.
    """
    service = ReportService(db)
    record = await service.get_report_by_id(report_id)
    return ReviewReportItem.model_validate(record)


@router.get("/download/{report_id}")
async def download_review_report_file(
    report_id: uuid.UUID,
    format: Optional[str] = Query("markdown", description="Export format: pdf, markdown, html, json"),
    db: AsyncSession = Depends(get_db),
):
    """
    Download executive review report formatted with appropriate content type and attachment headers.
    """
    service = ReportService(db)
    record = await service.get_report_by_id(report_id)

    fmt = (format or record.report_type or "markdown").lower().strip()
    metadata = record.report_metadata or {}
    repo_name = metadata.get("repository", "repository").replace("/", "_")
    pr_num = metadata.get("pr_number", 1)

    if fmt == "html":
        ext = ".html"
        media_type = "text/html"
        content = ProfessionalReportGeneratorEngine._render_html_report(record.report_title or "Report", metadata)
    elif fmt == "json":
        ext = ".json"
        media_type = "application/json"
        content = json.dumps(metadata, indent=2)
    elif fmt == "pdf":
        ext = ".pdf"
        media_type = "application/pdf"
        # Render HTML printable PDF payload
        content = ProfessionalReportGeneratorEngine._render_pdf_report(record.report_title or "Report", metadata)
    else:
        ext = ".md"
        media_type = "text/markdown"
        content = ProfessionalReportGeneratorEngine._render_markdown_report(record.report_title or "Report", metadata)

    filename = f"REVIEW_REPORT_{repo_name}_PR{pr_num}{ext}"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": f"{media_type}; charset=utf-8",
    }
    return Response(content=content, headers=headers, media_type=media_type)
