import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CommitActivityPoint(BaseModel):
    date: str
    count: int


class LanguageShare(BaseModel):
    language: str
    percentage: float
    color: str


class ContributorStats(BaseModel):
    author_name: str
    commits_count: int
    prs_count: int
    avatar_url: Optional[str] = None


class ReviewTimelineItem(BaseModel):
    id: uuid.UUID
    pr_number: int
    pr_title: str
    status: str
    quality_score: int
    findings_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepositoryHealthMetrics(BaseModel):
    health_score: int
    quality_score: int
    grade: str # A+, A, B, C, F
    security_issues_count: int
    performance_issues_count: int
    code_smells_count: int


class RepositoryAnalyticsResponse(BaseModel):
    repository_id: uuid.UUID
    full_name: str
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    health: RepositoryHealthMetrics
    languages: List[LanguageShare]
    commit_activity: List[CommitActivityPoint]
    contributors: List[ContributorStats]
    review_history: List[ReviewTimelineItem]


class DashboardMetricsResponse(BaseModel):
    total_repositories: int
    active_pull_requests: int
    total_commits_analyzed: int
    avg_quality_score: int
    security_score: int
    total_contributors: int
