import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TrendDataPoint(BaseModel):
    date: str
    quality_score: float
    security_issues: int
    performance_issues: int
    code_smells: int
    prs_reviewed: int


class QualityTrendsResponse(BaseModel):
    timeframe: str  # e.g., "7d", "30d", "90d", "1y"
    average_quality_score: float
    quality_improvement_percentage: float
    data: List[TrendDataPoint]


class RepositoryRankItem(BaseModel):
    rank: int
    repository_id: uuid.UUID
    full_name: str
    owner_login: str
    language: str
    quality_score: float
    health_grade: str  # e.g. "A+", "A", "B", "C", "F"
    stargazers_count: int
    open_issues_count: int
    prs_count: int
    security_vulnerabilities_count: int
    performance_bottlenecks_count: int


class RepositoryRankingsResponse(BaseModel):
    total_repositories: int
    rankings: List[RepositoryRankItem]


class ReviewHistoryItem(BaseModel):
    id: uuid.UUID
    pr_number: int
    pr_title: str
    repository_full_name: str
    author_login: str
    state: str  # "open", "closed", "merged"
    review_status: str  # "APPROVED", "CHANGES_REQUESTED", "COMMENTED", "IN_REVIEW"
    quality_score: float
    findings_count: int
    created_at: datetime
    html_url: Optional[str] = None


class ReviewHistoryResponse(BaseModel):
    total_reviews: int
    reviews: List[ReviewHistoryItem]


class IssueSeverityBreakdown(BaseModel):
    critical: int
    high: int
    medium: int
    low: int


class IssueCategoryBreakdown(BaseModel):
    security: int
    performance: int
    code_smell: int
    syntax_error: int


class IssueDistributionResponse(BaseModel):
    total_findings: int
    by_severity: IssueSeverityBreakdown
    by_category: IssueCategoryBreakdown
    by_language: Dict[str, int]
