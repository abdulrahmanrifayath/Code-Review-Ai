import time
import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.analysis import AnalysisResult
from app.models.findings import CodeSmell, PerformanceFinding, SecurityFinding
from app.models.pull_request import ChangedFile, PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.models.user import User
from app.schemas.analysis_dto import (
    AnalysisSummaryResponse,
    CodeSmellItem,
    PerformanceFindingItem,
    SecurityFindingItem,
)
from app.services.static_analysis.engine import StaticAnalysisEngine


class AnalysisService:
    """
    Service orchestrating static code analysis execution, Tree-sitter AST parsing,
    linter diagnostic collection, and PostgreSQL findings persistence.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_static_analysis(
        self, user: User, repository_id: uuid.UUID, pr_number: int
    ) -> AnalysisSummaryResponse:
        """
        Execute static analysis across all changed files of a Pull Request.
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

        # Get changed files
        cf_stmt = select(ChangedFile).where(ChangedFile.pull_request_id == pr.id)
        cf_res = await self.db.execute(cf_stmt)
        changed_files = list(cf_res.scalars().all())

        # Create or update ReviewJob
        job_stmt = select(ReviewJob).where(
            ReviewJob.pull_request_id == pr.id, ReviewJob.status == "QUEUED"
        )
        job_res = await self.db.execute(job_stmt)
        job = job_res.scalars().first()

        if not job:
            job = ReviewJob(
                pull_request_id=pr.id,
                status="PROCESSING",
                trigger_event="manual_analysis",
                started_at=pr.created_at,
            )
            self.db.add(job)
            await self.db.flush()

        job.status = "PROCESSING"
        self.db.add(job)

        start_time = time.time()

        # Create AnalysisResult container
        analysis_result = AnalysisResult(
            review_job_id=job.id,
            tool_name="tree-sitter + linters",
            category="static_analysis",
        )
        self.db.add(analysis_result)
        await self.db.flush()

        security_items: List[SecurityFindingItem] = []
        performance_items: List[PerformanceFindingItem] = []
        smell_items: List[CodeSmellItem] = []

        for cf in changed_files:
            code_content = cf.patch or ""
            language = cf.language or "Plain Text"

            findings = await StaticAnalysisEngine.analyze_code(cf.filename, code_content, language)

            # Persist Security Findings
            for sec in findings["security_findings"]:
                sf_obj = SecurityFinding(
                    analysis_result_id=analysis_result.id,
                    rule_id=sec["rule_id"],
                    title=sec["title"],
                    description=sec["description"],
                    severity=sec["severity"],
                    cwe_id=sec.get("cwe_id"),
                    file_path=sec["file_path"],
                    start_line=sec["start_line"],
                    end_line=sec["end_line"],
                    code_snippet=sec.get("code_snippet"),
                    remediation_suggestion=sec.get("remediation_suggestion"),
                )
                self.db.add(sf_obj)
                await self.db.flush()
                security_items.append(SecurityFindingItem.model_validate(sf_obj))

            # Persist Performance Findings
            for perf in findings["performance_findings"]:
                pf_obj = PerformanceFinding(
                    analysis_result_id=analysis_result.id,
                    rule_id=perf.get("rule_id"),
                    category=perf.get("category"),
                    title=perf["title"],
                    description=perf["description"],
                    impact_level=perf["impact_level"],
                    complexity_delta=perf.get("complexity_delta"),
                    suggestion_type=perf.get("suggestion_type"),
                    file_path=perf["file_path"],
                    start_line=perf["start_line"],
                    end_line=perf["end_line"],
                    code_snippet=perf.get("code_snippet"),
                    optimization_suggestion=perf.get("optimization_suggestion"),
                    structured_recommendation=perf.get("structured_recommendation"),
                )
                self.db.add(pf_obj)
                await self.db.flush()
                performance_items.append(PerformanceFindingItem.model_validate(pf_obj))

            # Persist Code Smells
            for smell in findings["code_smells"]:
                cs_obj = CodeSmell(
                    analysis_result_id=analysis_result.id,
                    smell_type=smell["smell_type"],
                    description=smell["description"],
                    severity=smell["severity"],
                    file_path=smell["file_path"],
                    start_line=smell["start_line"],
                    end_line=smell["end_line"],
                    refactoring_tip=smell.get("refactoring_tip"),
                )
                self.db.add(cs_obj)
                await self.db.flush()
                smell_items.append(CodeSmellItem.model_validate(cs_obj))

        execution_time_ms = int((time.time() - start_time) * 1000)
        analysis_result.execution_time_ms = execution_time_ms
        self.db.add(analysis_result)

        job.status = "COMPLETED"
        job.duration_seconds = max(1, execution_time_ms // 1000)
        self.db.add(job)
        await self.db.flush()

        total_findings = len(security_items) + len(performance_items) + len(smell_items)

        return AnalysisSummaryResponse(
            pull_request_id=pr.id,
            files_analyzed_count=len(changed_files),
            security_findings=security_items,
            performance_findings=performance_items,
            code_smells=smell_items,
            total_findings_count=total_findings,
        )

    async def get_pr_findings(
        self, repository_id: uuid.UUID, pr_number: int
    ) -> AnalysisSummaryResponse:
        """
        Retrieve stored static analysis findings for a Pull Request.
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

        # Query findings linked via ReviewJob -> AnalysisResult
        job_stmt = select(ReviewJob).where(ReviewJob.pull_request_id == pr.id).order_by(ReviewJob.created_at.desc())
        job_res = await self.db.execute(job_stmt)
        job = job_res.scalars().first()

        security_items: List[SecurityFindingItem] = []
        performance_items: List[PerformanceFindingItem] = []
        smell_items: List[CodeSmellItem] = []

        if job:
            ar_stmt = select(AnalysisResult).where(AnalysisResult.review_job_id == job.id)
            ar_res = await self.db.execute(ar_stmt)
            ar_results = list(ar_res.scalars().all())

            for ar in ar_results:
                sf_stmt = select(SecurityFinding).where(SecurityFinding.analysis_result_id == ar.id)
                sf_res = await self.db.execute(sf_stmt)
                for sf in sf_res.scalars().all():
                    security_items.append(SecurityFindingItem.model_validate(sf))

                pf_stmt = select(PerformanceFinding).where(PerformanceFinding.analysis_result_id == ar.id)
                pf_res = await self.db.execute(pf_stmt)
                for pf in pf_res.scalars().all():
                    performance_items.append(PerformanceFindingItem.model_validate(pf))

                cs_stmt = select(CodeSmell).where(CodeSmell.analysis_result_id == ar.id)
                cs_res = await self.db.execute(cs_stmt)
                for cs in cs_res.scalars().all():
                    smell_items.append(CodeSmellItem.model_validate(cs))

        total_findings = len(security_items) + len(performance_items) + len(smell_items)

        return AnalysisSummaryResponse(
            pull_request_id=pr.id,
            files_analyzed_count=pr.changed_files_count,
            security_findings=security_items,
            performance_findings=performance_items,
            code_smells=smell_items,
            total_findings_count=total_findings,
        )
