import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.schemas.analytics_dto import (
    IssueCategoryBreakdown,
    IssueDistributionResponse,
    IssueSeverityBreakdown,
    QualityTrendsResponse,
    RepositoryRankingsResponse,
    ReviewHistoryResponse,
    TrendDataPoint,
)
from app.services.repository_analytics import RepositoryAnalyticsService


class TestAnalyticsAPI(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_result.scalars.return_value.all.return_value = []
        mock_result.all.return_value = []
        self.db.execute.return_value = mock_result
        self.service = RepositoryAnalyticsService(self.db)

    async def test_get_quality_trends(self):
        res = await self.service.get_quality_trends("30d")
        self.assertIsInstance(res, QualityTrendsResponse)
        self.assertEqual(res.timeframe, "30d")
        self.assertGreater(len(res.data), 0)
        self.assertIsInstance(res.data[0], TrendDataPoint)

    async def test_get_repository_rankings(self):
        res = await self.service.get_repository_rankings()
        self.assertIsInstance(res, RepositoryRankingsResponse)
        self.assertGreater(res.total_repositories, 0)
        self.assertEqual(res.rankings[0].rank, 1)

    async def test_get_review_history(self):
        res = await self.service.get_review_history(search=None, status="ALL", limit=10)
        self.assertIsInstance(res, ReviewHistoryResponse)
        self.assertGreater(res.total_reviews, 0)

        # Test search filter
        filtered = await self.service.get_review_history(search="redis", status="ALL", limit=10)
        self.assertIsInstance(filtered, ReviewHistoryResponse)

    async def test_get_issue_distribution(self):
        res = await self.service.get_issue_distribution()
        self.assertIsInstance(res, IssueDistributionResponse)
        self.assertGreater(res.total_findings, 0)
        self.assertIsInstance(res.by_severity, IssueSeverityBreakdown)
        self.assertIsInstance(res.by_category, IssueCategoryBreakdown)


if __name__ == "__main__":
    unittest.main()
