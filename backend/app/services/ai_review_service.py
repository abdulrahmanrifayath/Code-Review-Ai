import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.activity import ReviewHistory
from app.models.ai_review import AIReview
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.models.user import User
from app.schemas.ai_review_dto import AIReviewResponse
from app.services.ai_review.context_builder import AIReviewContextBuilder
from app.services.ai_review.engine import AIReviewEngine


class AIReviewService:
    """
    Service coordinating AI Review generation, LLM context building,
    and PostgreSQL persistence for AIReview and ReviewHistory entities.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_ai_review(
        self, user: User, repository_id: uuid.UUID, pr_number: int
    ) -> AIReviewResponse:
        """
        Build PR context, run AI review analysis engine, store AIReview entity,
        and record ReviewHistory audit log.
        """
        repo_stmt = select(Repository).where(Repository.id == repository_id)
        repo_res = await self.db.execute(repo_stmt)
        repo = repo_res.scalars().first()
        if not repo:
            raise NotFoundError("Repository", repository_id)

        pr_stmt = select(PullRequest).where(
            PullRequest.repository_id == repository_id, PullRequest.pr_number == pr_number
        )
        pr_res = await self.db.execute(pr_stmt)
        pr = pr_res.scalars().first()
        if not pr:
            raise NotFoundError("PullRequest", pr_number)

        # Build Context
        context_builder = AIReviewContextBuilder(self.db)
        context = await context_builder.build_pr_review_context(repository_id, pr_number)

        # Run AI Review Engine
        raw_review = await AIReviewEngine.run_ai_review(context)

        # Persist AIReview entity
        ai_review_obj = AIReview(
            pull_request_id=pr.id,
            summary=raw_review["summary"],
            bugs=raw_review["findings"], # JSON array
            security_issues=raw_review["findings"], # JSON array
            performance_notes=raw_review["findings"],
            code_smells=raw_review["findings"],
            suggested_tests=[],
            suggested_docs="",
        )
        self.db.add(ai_review_obj)
        await self.db.flush()

        # Add ReviewHistory audit log
        history_entry = ReviewHistory(
            pull_request_id=pr.id,
            user_id=user.id,
            action="AI_REVIEW_GENERATED",
            status="completed",
            quality_score=raw_review["score"],
            findings_count=len(raw_review["findings"]),
            comments=raw_review["summary"],
        )
        self.db.add(history_entry)

        # Update ReviewJob status
        job_stmt = select(ReviewJob).where(ReviewJob.pull_request_id == pr.id).order_by(ReviewJob.created_at.desc())
        job_res = await self.db.execute(job_stmt)
        job = job_res.scalars().first()
        if job:
            job.status = "COMPLETED"
            self.db.add(job)

        await self.db.flush()

        return AIReviewResponse(
            id=ai_review_obj.id,
            pull_request_id=pr.id,
            summary=raw_review["summary"],
            quality_score=raw_review["score"],
            recommendation=raw_review["recommendation"],
            findings=raw_review["findings"],
            inline_comments=raw_review["inline_comments"],
            created_at=ai_review_obj.created_at,
        )

    async def get_latest_ai_review(
        self, repository_id: uuid.UUID, pr_number: int
    ) -> AIReviewResponse:
        """
        Fetch latest AI review for a Pull Request from database.
        """
        repo_stmt = select(Repository).where(Repository.id == repository_id)
        repo_res = await self.db.execute(repo_stmt)
        repo = repo_res.scalars().first()
        if not repo:
            raise NotFoundError("Repository", repository_id)

        pr_stmt = select(PullRequest).where(
            PullRequest.repository_id == repository_id, PullRequest.pr_number == pr_number
        )
        pr_res = await self.db.execute(pr_stmt)
        pr = pr_res.scalars().first()
        if not pr:
            raise NotFoundError("PullRequest", pr_number)

        rev_stmt = select(AIReview).where(AIReview.pull_request_id == pr.id).order_by(AIReview.created_at.desc())
        rev_res = await self.db.execute(rev_stmt)
        ai_review_obj = rev_res.scalars().first()

        if not ai_review_obj:
            raise NotFoundError("AIReview for PR", pr_number)

        findings = ai_review_obj.bugs or []

        return AIReviewResponse(
            id=ai_review_obj.id,
            pull_request_id=pr.id,
            summary=ai_review_obj.summary,
            quality_score=85,
            recommendation="COMMENT",
            findings=findings,
            inline_comments=[],
            created_at=ai_review_obj.created_at,
        )
