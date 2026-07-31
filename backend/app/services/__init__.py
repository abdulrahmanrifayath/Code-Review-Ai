"""
Services Package containing domain business logic interfaces.
"""
from app.services.base import BaseService

try:
    from app.services.auth import AuthService
    from app.services.github import GitHubService
    from app.services.ai_review import AIReviewService
    __all__ = ["BaseService", "AuthService", "GitHubService", "AIReviewService"]
except ImportError:
    __all__ = ["BaseService"]
