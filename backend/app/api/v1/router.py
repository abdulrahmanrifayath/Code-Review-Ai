from fastapi import APIRouter
from app.api.v1.endpoints import auth, github, health, repositories, reviews, webhooks

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(github.router, prefix="/github", tags=["GitHub Integration"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repositories"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Code Reviews"])
