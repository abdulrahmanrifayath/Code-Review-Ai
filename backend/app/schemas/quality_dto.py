import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CodeQualityMetrics(BaseModel):
    maintainability_score: int # 0 - 100
    technical_debt_hours: float # estimated debt in hours
    complexity_score: float # average cyclomatic complexity
    doc_coverage_percentage: float # 0.0 - 100.0%
    architecture_score: int # 0 - 100
    overall_quality_score: int # 0 - 100
    grade: str # A+, A, B, C, F


class QualityTrendPoint(BaseModel):
    date: str
    maintainability_score: int
    technical_debt_hours: float
    complexity_score: float
    doc_coverage_percentage: float
    architecture_score: int
    overall_quality_score: int


class PRQualityScoreResponse(BaseModel):
    pull_request_id: uuid.UUID
    pr_number: int
    pr_title: str
    quality_score: int
    grade: str
    metrics: CodeQualityMetrics
    findings_summary: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RepoQualityScoreResponse(BaseModel):
    repository_id: uuid.UUID
    repository_full_name: str
    current_quality_score: int
    grade: str
    metrics: CodeQualityMetrics
    latest_trends: list[QualityTrendPoint]

    model_config = ConfigDict(from_attributes=True)


class QualityHistoryResponse(BaseModel):
    repository_id: uuid.UUID
    total_snapshots: int
    trends: list[QualityTrendPoint]
