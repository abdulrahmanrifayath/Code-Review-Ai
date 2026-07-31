import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class PerformanceFindingItem(BaseModel):
    id: Optional[uuid.UUID] = None
    rule_id: Optional[str] = None
    category: Optional[str] = None # Nested loops, Repeated DB queries, Blocking operations, Large memory allocations, Repeated API calls, Expensive regex
    title: str
    description: str
    impact_level: str # HIGH, MEDIUM, LOW
    complexity_delta: Optional[str] = None # e.g. O(N^2) -> O(N)
    suggestion_type: Optional[str] = None # Caching, Pagination, Indexes, Async, Lazy loading
    file_path: str
    start_line: int
    end_line: int
    code_snippet: Optional[str] = None
    optimization_suggestion: Optional[str] = None
    structured_recommendation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PerformanceAnalysisSummaryResponse(BaseModel):
    pull_request_id: Optional[uuid.UUID] = None
    files_analyzed_count: int
    findings: List[PerformanceFindingItem]
    total_findings_count: int
    high_impact_count: int
    medium_impact_count: int
    low_impact_count: int
    category_breakdown: dict
    suggestion_breakdown: dict
