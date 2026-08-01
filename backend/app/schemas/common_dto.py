from datetime import UTC, datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationQueryParams(BaseModel):
    page: int = Field(1, ge=1, description="1-indexed page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page (max 100)")
    sort_by: str | None = Field(None, description="Field name to sort by")
    order: str = Field("desc", regex="^(asc|desc)$", description="Sort direction: asc or desc")


class APIResponse(BaseModel, Generic[T]):
    code: int = Field(200, description="HTTP status code")
    message: str = Field("Success", description="User-facing message")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    data: T | None = None


class PaginatedListResponse(BaseModel, Generic[T]):
    total_count: int = Field(..., ge=0)
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1)
    total_pages: int = Field(..., ge=0)
    items: list[T]
