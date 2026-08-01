
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import (
    clear_auth_cookies,
    get_auth_service,
    get_current_user,
    require_role,
    set_auth_cookies,
)
from app.core.errors import UnauthorizedError
from app.models.user import User
from app.schemas.auth import (
    GitHubAuthCode,
    GitHubOAuthUrlResponse,
    RefreshRequest,
    TokenResponse,
    UserAuthResponse,
)
from app.schemas.user import UserCreate
from app.services.auth import AuthService
from app.services.github_oauth import GitHubOAuthService

router = APIRouter()


@router.post("/register", response_model=UserAuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user account."""
    user = await auth_service.register_user(user_in)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Local username/email and password login endpoint."""
    user = await auth_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )
    user_agent = request.headers.get("User-Agent")
    client_ip = request.client.host if request.client else None

    access_token, refresh_token, expires_in = await auth_service.create_session_and_tokens(
        user, user_agent=user_agent, ip_address=client_ip
    )

    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.get("/github/url", response_model=GitHubOAuthUrlResponse)
async def get_github_oauth_url():
    """Generate GitHub OAuth 2.0 authorization URL and anti-CSRF state token."""
    github_service = GitHubOAuthService()
    url, state = github_service.get_authorization_url()
    return GitHubOAuthUrlResponse(url=url, state=state)


@router.post("/github/callback", response_model=TokenResponse)
async def github_oauth_callback(
    payload: GitHubAuthCode,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Process GitHub OAuth authorization code and authenticate user."""
    user_agent = request.headers.get("User-Agent")
    client_ip = request.client.host if request.client else None

    user, access_token, refresh_token, expires_in = await auth_service.authenticate_github_user(
        code=payload.code, user_agent=user_agent, ip_address=client_ip
    )

    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: Request,
    response: Response,
    refresh_payload: RefreshRequest | None = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Refresh JWT access token using HttpOnly refresh token cookie or request payload.
    Rotates refresh token for security.
    """
    refresh_token = (
        request.cookies.get("refresh_token")
        or (refresh_payload.refresh_token if refresh_payload else None)
    )

    if not refresh_token:
        raise UnauthorizedError("Refresh token missing.")

    user_agent = request.headers.get("User-Agent")
    client_ip = request.client.host if request.client else None

    access_token, new_refresh_token, expires_in, user = await auth_service.refresh_session_tokens(
        refresh_token_str=refresh_token, user_agent=user_agent, ip_address=client_ip
    )

    set_auth_cookies(response, access_token, new_refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Revoke active user session and clear authentication cookies."""
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await auth_service.logout_session(refresh_token)

    clear_auth_cookies(response)
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=UserAuthResponse)
async def read_current_user_profile(current_user: User = Depends(get_current_user)):
    """Fetch authenticated user profile."""
    return current_user


@router.get("/admin-only", response_model=UserAuthResponse)
async def admin_only_endpoint(current_user: User = Depends(require_role("ADMIN"))):
    """Protected endpoint restricted strictly to Admin users (RBAC demonstration)."""
    return current_user
