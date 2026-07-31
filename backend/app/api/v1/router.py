from fastapi import APIRouter
from app.api.v1.endpoints import (
    analysis,
    auth,
    doc_generator,
    github,
    health,
    parser,
    performance,
    quality,
    reports,
    repositories,
    reviews,
    security,
    test_generator,
    webhooks,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(github.router, prefix="/github", tags=["GitHub Integration"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(parser.router, prefix="/parser", tags=["Diff Parser"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["Static Analysis"])
api_router.include_router(security.router, prefix="/security", tags=["Security Analyzer"])
api_router.include_router(performance.router, prefix="/performance", tags=["Performance Analyzer"])
api_router.include_router(quality.router, prefix="/quality", tags=["Code Quality Engine"])
api_router.include_router(test_generator.router, prefix="/tests", tags=["AI Test Generator"])
api_router.include_router(doc_generator.router, prefix="/docs", tags=["AI Documentation Generator"])
api_router.include_router(reports.router, prefix="/reports", tags=["Professional Review Reports"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositories"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Code Reviews"])
