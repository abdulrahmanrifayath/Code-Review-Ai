import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.artifacts import ReviewReport
from app.models.pull_request import PullRequest
from app.schemas.report_dto import (
    ReportGenerationRequest,
    ReportGeneratorResponse,
    ReviewReportItem,
)
from app.services.reports.report_generator import ProfessionalReportGeneratorEngine


class ReportService:
    """
    Service managing executive review report generation, database persistence in ReviewReport table,
    and formatted export downloads.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_and_save_report(
        self, request: ReportGenerationRequest
    ) -> ReportGeneratorResponse:
        """
        Generate executive review report for given repository/PR, persist snapshot to DB, and return response DTO.
        """
        pr_id: uuid.UUID | None = request.pull_request_id
        if pr_id:
            pr_stmt = select(PullRequest).where(PullRequest.id == pr_id)
            pr_res = await self.db.execute(pr_stmt)
            if not pr_res.scalars().first():
                pr_id = None

        content, title, metadata = ProfessionalReportGeneratorEngine.generate_report(
            repository_full_name=request.repository_full_name,
            pr_number=request.pr_number or 1,
            format_type=request.format,
        )

        report_record = ReviewReport(
            pull_request_id=pr_id,
            report_type=request.format.upper(),
            report_title=title,
            content=content,
            report_metadata=metadata,
        )
        self.db.add(report_record)
        await self.db.flush()

        download_url = f"/api/v1/reports/download/{report_record.id}?format={request.format.lower()}"

        return ReportGeneratorResponse(
            report_id=report_record.id,
            repository_full_name=request.repository_full_name,
            pr_number=request.pr_number or 1,
            report_type=report_record.report_type,
            report_title=report_record.report_title or title,
            content=report_record.content or "",
            report_metadata=report_record.report_metadata or {},
            download_url=download_url,
            created_at=report_record.created_at,
        )

    async def get_report_by_id(self, report_id: uuid.UUID) -> ReviewReport:
        """
        Retrieve a single review report record by ID.
        """
        stmt = select(ReviewReport).where(ReviewReport.id == report_id)
        res = await self.db.execute(stmt)
        record = res.scalars().first()
        if not record:
            raise NotFoundError("ReviewReport", report_id)
        return record

    async def get_pr_reports(self, pr_id: uuid.UUID) -> list[ReviewReportItem]:
        """
        Fetch all generated review report records associated with a Pull Request.
        """
        stmt = select(ReviewReport).where(ReviewReport.pull_request_id == pr_id).order_by(ReviewReport.created_at.desc())
        res = await self.db.execute(stmt)
        records = list(res.scalars().all())
        return [ReviewReportItem.model_validate(r) for r in records]
