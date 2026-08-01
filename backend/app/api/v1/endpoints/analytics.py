from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.analytics_dto import (
    IssueDistributionResponse,
    QualityTrendsResponse,
    RepositoryRankingsResponse,
    ReviewHistoryResponse,
)
from app.services.repository_analytics import RepositoryAnalyticsService

router = APIRouter()


@router.get("/trends", response_model=QualityTrendsResponse, status_code=status.HTTP_200_OK)
async def get_quality_trends(
    timeframe: str = Query("30d", description="Timeframe: 7d, 30d, 90d, 1y"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves historical quality, security, and performance trend points over time.
    """
    service = RepositoryAnalyticsService(db)
    return await service.get_quality_trends(timeframe=timeframe)


@router.get("/rankings", response_model=RepositoryRankingsResponse, status_code=status.HTTP_200_OK)
async def get_repository_rankings(
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves repository leaderboard ranked by code quality score and health metrics.
    """
    service = RepositoryAnalyticsService(db)
    return await service.get_repository_rankings()


@router.get("/history", response_model=ReviewHistoryResponse, status_code=status.HTTP_200_OK)
async def get_review_history(
    search: Optional[str] = Query(None, description="Search query by PR title, repo, or author"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter status: ALL, APPROVED, CHANGES_REQUESTED"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves searchable, filterable code review audit history.
    """
    service = RepositoryAnalyticsService(db)
    return await service.get_review_history(search=search, status=status_filter, limit=limit)


@router.get("/issues-distribution", response_model=IssueDistributionResponse, status_code=status.HTTP_200_OK)
async def get_issue_distribution(
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves issue breakdown by severity (Critical, High, Medium, Low) and category.
    """
    service = RepositoryAnalyticsService(db)
    return await service.get_issue_distribution()
