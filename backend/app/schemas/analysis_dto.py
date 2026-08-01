import uuid

from pydantic import BaseModel, ConfigDict


class SecurityFindingItem(BaseModel):
    id: uuid.UUID | None = None
    rule_id: str
    title: str
    description: str
    severity: str # CRITICAL, HIGH, MEDIUM, LOW
    cwe_id: str | None = None
    file_path: str
    start_line: int
    end_line: int
    code_snippet: str | None = None
    remediation_suggestion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PerformanceFindingItem(BaseModel):
    id: uuid.UUID | None = None
    title: str
    description: str
    impact_level: str # HIGH, MEDIUM, LOW
    complexity_delta: str | None = None
    file_path: str
    start_line: int
    end_line: int
    code_snippet: str | None = None
    optimization_suggestion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CodeSmellItem(BaseModel):
    id: uuid.UUID | None = None
    smell_type: str
    description: str
    severity: str # INFO, WARNING, ERROR
    file_path: str
    start_line: int
    end_line: int
    refactoring_tip: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisSummaryResponse(BaseModel):
    pull_request_id: uuid.UUID
    files_analyzed_count: int
    security_findings: list[SecurityFindingItem]
    performance_findings: list[PerformanceFindingItem]
    code_smells: list[CodeSmellItem]
    total_findings_count: int
