import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SecurityFindingItem(BaseModel):
    id: Optional[uuid.UUID] = None
    rule_id: str
    title: str
    description: str
    severity: str # CRITICAL, HIGH, MEDIUM, LOW
    cwe_id: Optional[str] = None
    file_path: str
    start_line: int
    end_line: int
    code_snippet: Optional[str] = None
    remediation_suggestion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PerformanceFindingItem(BaseModel):
    id: Optional[uuid.UUID] = None
    title: str
    description: str
    impact_level: str # HIGH, MEDIUM, LOW
    complexity_delta: Optional[str] = None
    file_path: str
    start_line: int
    end_line: int
    code_snippet: Optional[str] = None
    optimization_suggestion: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CodeSmellItem(BaseModel):
    id: Optional[uuid.UUID] = None
    smell_type: str
    description: str
    severity: str # INFO, WARNING, ERROR
    file_path: str
    start_line: int
    end_line: int
    refactoring_tip: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisSummaryResponse(BaseModel):
    pull_request_id: uuid.UUID
    files_analyzed_count: int
    security_findings: List[SecurityFindingItem]
    performance_findings: List[PerformanceFindingItem]
    code_smells: List[CodeSmellItem]
    total_findings_count: int
