import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.analysis import AnalysisResult
from app.models.findings import SecurityFinding
from app.models.pull_request import ChangedFile, PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.models.user import User
from app.schemas.security_dto import SecurityDashboardSummaryResponse, SecurityFindingDetailResponse
from app.services.security_analyzer.engine import SecurityAnalyzerEngine


class SecurityAnalysisService:
    """
    Service for executing SAST security scans and building Security Dashboard data.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_security_scan(
        self, user: User, repository_id: uuid.UUID, pr_number: int
    ) -> SecurityDashboardSummaryResponse:
        """
        Scan all changed files of a Pull Request for SAST vulnerabilities.
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

        # Get or create ReviewJob
        job_stmt = select(ReviewJob).where(ReviewJob.pull_request_id == pr.id).order_by(ReviewJob.created_at.desc())
        job_res = await self.db.execute(job_stmt)
        job = job_res.scalars().first()

        if not job:
            job = ReviewJob(pull_request_id=pr.id, status="PROCESSING", trigger_event="security_scan")
            self.db.add(job)
            await self.db.flush()

        analysis_result = AnalysisResult(
            review_job_id=job.id,
            tool_name="sast-security-analyzer",
            category="security_scan",
        )
        self.db.add(analysis_result)
        await self.db.flush()

        finding_items: List[SecurityFindingDetailResponse] = []

        for cf in changed_files:
            code_content = cf.patch or ""
            raw_findings = SecurityAnalyzerEngine.scan_file_content(cf.filename, code_content)

            for raw in raw_findings:
                sf_obj = SecurityFinding(
                    analysis_result_id=analysis_result.id,
                    rule_id=raw["rule_id"],
                    title=raw["title"],
                    description=raw["description"],
                    severity=raw["severity"],
                    cwe_id=raw["cwe_id"],
                    file_path=raw["file_path"],
                    start_line=raw["line_number"],
                    end_line=raw["line_number"],
                    code_snippet=raw.get("code_snippet"),
                    remediation_suggestion=raw.get("remediation_suggestion"),
                )
                self.db.add(sf_obj)
                await self.db.flush()

                finding_items.append(
                    SecurityFindingDetailResponse(
                        id=sf_obj.id,
                        rule_id=sf_obj.rule_id,
                        category=raw["category"],
                        cwe_id=sf_obj.cwe_id,
                        severity=sf_obj.severity,
                        title=sf_obj.title,
                        description=sf_obj.description,
                        file_path=sf_obj.file_path,
                        line_number=sf_obj.start_line,
                        code_snippet=sf_obj.code_snippet,
                        remediation_suggestion=sf_obj.remediation_suggestion,
                    )
                )

        crit_cnt = sum(1 for item in finding_items if item.severity == "CRITICAL")
        high_cnt = sum(1 for item in finding_items if item.severity == "HIGH")
        med_cnt = sum(1 for item in finding_items if item.severity == "MEDIUM")
        low_cnt = sum(1 for item in finding_items if item.severity == "LOW")

        return SecurityDashboardSummaryResponse(
            repository_full_name=repo.full_name,
            pr_number=pr.pr_number,
            total_vulnerabilities_count=len(finding_items),
            critical_count=crit_cnt,
            high_count=high_cnt,
            medium_count=med_cnt,
            low_count=low_cnt,
            findings=finding_items,
        )

    async def get_security_dashboard(
        self, repository_id: uuid.UUID, pr_number: int
    ) -> SecurityDashboardSummaryResponse:
        """
        Fetch Security Dashboard data for a PR.
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

        job_stmt = select(ReviewJob).where(ReviewJob.pull_request_id == pr.id).order_by(ReviewJob.created_at.desc())
        job_res = await self.db.execute(job_stmt)
        job = job_res.scalars().first()

        finding_items: List[SecurityFindingDetailResponse] = []

        if job:
            ar_stmt = select(AnalysisResult).where(AnalysisResult.review_job_id == job.id)
            ar_res = await self.db.execute(ar_stmt)
            ar_results = list(ar_res.scalars().all())

            for ar in ar_results:
                sf_stmt = select(SecurityFinding).where(SecurityFinding.analysis_result_id == ar.id)
                sf_res = await self.db.execute(sf_stmt)
                for sf in sf_res.scalars().all():
                    category = "Vulnerability"
                    if "SQL" in sf.rule_id:
                        category = "SQL Injection"
                    elif "CRED" in sf.rule_id:
                        category = "Hardcoded Credentials"
                    elif "KEY" in sf.rule_id:
                        category = "API Keys"
                    elif "JWT" in sf.rule_id:
                        category = "JWT Issues"
                    elif "CMD" in sf.rule_id:
                        category = "Command Injection"
                    elif "FILE" in sf.rule_id:
                        category = "Unsafe File Operations"
                    elif "XSS" in sf.rule_id:
                        category = "XSS"
                    elif "CSRF" in sf.rule_id:
                        category = "CSRF"
                    elif "PATH" in sf.rule_id:
                        category = "Path Traversal"

                    finding_items.append(
                        SecurityFindingDetailResponse(
                            id=sf.id,
                            rule_id=sf.rule_id,
                            category=category,
                            cwe_id=sf.cwe_id or "CWE-200",
                            severity=sf.severity,
                            title=sf.title,
                            description=sf.description,
                            file_path=sf.file_path,
                            line_number=sf.start_line,
                            code_snippet=sf.code_snippet,
                            remediation_suggestion=sf.remediation_suggestion,
                        )
                    )

        crit_cnt = sum(1 for item in finding_items if item.severity == "CRITICAL")
        high_cnt = sum(1 for item in finding_items if item.severity == "HIGH")
        med_cnt = sum(1 for item in finding_items if item.severity == "MEDIUM")
        low_cnt = sum(1 for item in finding_items if item.severity == "LOW")

        return SecurityDashboardSummaryResponse(
            repository_full_name=repo.full_name,
            pr_number=pr.pr_number,
            total_vulnerabilities_count=len(finding_items),
            critical_count=crit_cnt,
            high_count=high_cnt,
            medium_count=med_cnt,
            low_count=low_cnt,
            findings=finding_items,
        )
