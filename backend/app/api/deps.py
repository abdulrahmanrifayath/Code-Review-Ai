import uuid
from collections.abc import Callable

import jwt
from fastapi import Depends, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import ForbiddenError, UnauthorizedError
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(user_repo, db)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    header_token: str | None = Depends(reusable_oauth2),
) -> User:
    """
    Dependency to resolve authenticated user from Bearer header OR HttpOnly cookie.
    """
    token = header_token or request.cookies.get("access_token")
    if not token:
        raise UnauthorizedError("Authentication token missing.")

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise UnauthorizedError("Invalid authentication token payload.")
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise UnauthorizedError("Could not validate authentication token.")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedError("User associated with token not found.")
    if not user.is_active:
        raise UnauthorizedError("User account is disabled.")

    return user


def require_role(*allowed_roles: str) -> Callable:
    """
    Dependency factory enforcing Role-Based Access Control (RBAC).
    Allowed Roles: 'ADMIN', 'REVIEWER', 'DEVELOPER'
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser or current_user.role == "ADMIN":
            return current_user

        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"Role '{current_user.role}' is not authorized to access this resource. Required: {list(allowed_roles)}"
            )
        return current_user

    return role_checker


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """
    Set secure, HttpOnly cookies on the HTTP response for access and refresh tokens.
    """
    # Access Token Cookie (60 mins)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    # Refresh Token Cookie (7 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=f"{settings.API_V1_STR}/auth/refresh",
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear access and refresh token cookies from browser."""
    response.delete_cookie(key="access_token", samesite="lax")
    response.delete_cookie(key="refresh_token", path=f"{settings.API_V1_STR}/auth/refresh", samesite="lax")
