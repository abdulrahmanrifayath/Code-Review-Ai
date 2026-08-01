import uuid

from pydantic import BaseModel, ConfigDict


class PerformanceFindingItem(BaseModel):
    id: uuid.UUID | None = None
    rule_id: str | None = None
    category: str | None = None # Nested loops, Repeated DB queries, Blocking operations, Large memory allocations, Repeated API calls, Expensive regex
    title: str
    description: str
    impact_level: str # HIGH, MEDIUM, LOW
    complexity_delta: str | None = None # e.g. O(N^2) -> O(N)
    suggestion_type: str | None = None # Caching, Pagination, Indexes, Async, Lazy loading
    file_path: str
    start_line: int
    end_line: int
    code_snippet: str | None = None
    optimization_suggestion: str | None = None
    structured_recommendation: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PerformanceAnalysisSummaryResponse(BaseModel):
    pull_request_id: uuid.UUID | None = None
    files_analyzed_count: int
    findings: list[PerformanceFindingItem]
    total_findings_count: int
    high_impact_count: int
    medium_impact_count: int
    low_impact_count: int
    category_breakdown: dict
    suggestion_breakdown: dict
