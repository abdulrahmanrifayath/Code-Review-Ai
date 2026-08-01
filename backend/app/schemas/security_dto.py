import uuid

from pydantic import BaseModel, ConfigDict


class SecurityFindingDetailResponse(BaseModel):
    id: uuid.UUID | None = None
    rule_id: str
    category: str
    cwe_id: str
    severity: str # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str | None = None
    remediation_suggestion: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SecurityDashboardSummaryResponse(BaseModel):
    repository_full_name: str
    pr_number: int
    total_vulnerabilities_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings: list[SecurityFindingDetailResponse]
