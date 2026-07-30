from typing import List
from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.review import CodeReviewResponse

router = APIRouter()


@router.get("", response_model=List[CodeReviewResponse])
async def list_reviews(current_user: User = Depends(get_current_user)):
    """List code reviews generated for connected repositories."""
    return []
