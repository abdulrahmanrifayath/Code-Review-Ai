import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict


class DiffLineItem(BaseModel):
    line_number: int
    type: str # add, delete, context
    content: str


class DiffHunkItem(BaseModel):
    header: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    heading: str
    lines: list[dict[str, Any]]


class ParsedFileDiffResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    language: str | None = None
    additions: int
    deletions: int
    patch: str | None = None
    parsed_diff: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class ParsedPRSummaryResponse(BaseModel):
    repository_full_name: str
    pr_number: int
    pr_title: str
    changed_files_count: int
    total_additions: int
    total_deletions: int
    languages_detected: list[str]
    files: list[ParsedFileDiffResponse]
