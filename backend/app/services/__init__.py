"""
Services Package containing domain business logic interfaces.
"""
from app.services.base import BaseService

try:
    from app.services.ai_review_service import AIReviewService
    from app.services.auth import AuthService
    from app.services.github import GitHubService
    __all__ = ["AIReviewService", "AuthService", "BaseService", "GitHubService"]
except ImportError:
    __all__ = ["BaseService"]
