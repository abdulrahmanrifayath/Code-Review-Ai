from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotFoundError
from app.models.analysis import AnalysisResult
from app.models.findings import PerformanceFinding
from app.models.pull_request import ChangedFile, PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.schemas.performance_dto import PerformanceAnalysisSummaryResponse, PerformanceFindingItem
from app.services.performance_analyzer.engine import PerformanceAnalyzerEngine

router = APIRouter()


@router.post("/repos/{owner}/{repo}/pulls/{number}/scan", response_model=PerformanceAnalysisSummaryResponse)
async def scan_pull_request_performance(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute Performance Analyzer engine scanning for Nested Loops, Repeated DB Queries,
    Blocking Operations, Large Memory Allocations, Repeated API Calls, and Expensive Regex.
    Returns structured recommendations (Caching, Pagination, Indexes, Async, Lazy loading).
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

    cf_stmt = select(ChangedFile).where(ChangedFile.pull_request_id == pr.id)
    cf_res = await db.execute(cf_stmt)
    changed_files = list(cf_res.scalars().all())

    all_findings: list[PerformanceFindingItem] = []
    category_breakdown: dict[str, int] = {}
    suggestion_breakdown: dict[str, int] = {}

    high_count = 0
    med_count = 0
    low_count = 0

    for cf in changed_files:
        code_content = cf.patch or ""
        file_findings = PerformanceAnalyzerEngine.analyze_file_performance(cf.filename, code_content)
        for f in file_findings:
            item = PerformanceFindingItem(
                rule_id=f.get("rule_id"),
                category=f.get("category"),
                title=f["title"],
                description=f["description"],
                impact_level=f["impact_level"],
                complexity_delta=f.get("complexity_delta"),
                suggestion_type=f.get("suggestion_type"),
                file_path=f["file_path"],
                start_line=f["start_line"],
                end_line=f["end_line"],
                code_snippet=f.get("code_snippet"),
                optimization_suggestion=f.get("optimization_suggestion"),
                structured_recommendation=f.get("structured_recommendation"),
            )
            all_findings.append(item)

            cat = f.get("category", "Other")
            category_breakdown[cat] = category_breakdown.get(cat, 0) + 1

            sug = f.get("suggestion_type", "General Optimization")
            suggestion_breakdown[sug] = suggestion_breakdown.get(sug, 0) + 1

            if f["impact_level"] == "HIGH":
                high_count += 1
            elif f["impact_level"] == "MEDIUM":
                med_count += 1
            else:
                low_count += 1

    return PerformanceAnalysisSummaryResponse(
        pull_request_id=pr.id,
        files_analyzed_count=len(changed_files),
        findings=all_findings,
        total_findings_count=len(all_findings),
        high_impact_count=high_count,
        medium_impact_count=med_count,
        low_impact_count=low_count,
        category_breakdown=category_breakdown,
        suggestion_breakdown=suggestion_breakdown,
    )


@router.get("/repos/{owner}/{repo}/pulls/{number}/findings", response_model=PerformanceAnalysisSummaryResponse)
async def get_pull_request_performance_findings(
    owner: str,
    repo: str,
    number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve stored Performance Analyzer findings and structured recommendations.
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

    all_findings: list[PerformanceFindingItem] = []
    category_breakdown: dict[str, int] = {}
    suggestion_breakdown: dict[str, int] = {}
    high_count, med_count, low_count = 0, 0, 0

    ar_stmt = select(AnalysisResult).where(AnalysisResult.review_job_id == pr.id)
    ar_res = await db.execute(ar_stmt)
    ar_results = list(ar_res.scalars().all())

    for ar in ar_results:
        pf_stmt = select(PerformanceFinding).where(PerformanceFinding.analysis_result_id == ar.id)
        pf_res = await db.execute(pf_stmt)
        for pf in pf_res.scalars().all():
            item = PerformanceFindingItem.model_validate(pf)
            all_findings.append(item)

            cat = pf.category or "Other"
            category_breakdown[cat] = category_breakdown.get(cat, 0) + 1

            sug = pf.suggestion_type or "General Optimization"
            suggestion_breakdown[sug] = suggestion_breakdown.get(sug, 0) + 1

            if pf.impact_level == "HIGH":
                high_count += 1
            elif pf.impact_level == "MEDIUM":
                med_count += 1
            else:
                low_count += 1

    return PerformanceAnalysisSummaryResponse(
        pull_request_id=pr.id,
        files_analyzed_count=pr.changed_files_count,
        findings=all_findings,
        total_findings_count=len(all_findings),
        high_impact_count=high_count,
        medium_impact_count=med_count,
        low_impact_count=low_count,
        category_breakdown=category_breakdown,
        suggestion_breakdown=suggestion_breakdown,
    )
