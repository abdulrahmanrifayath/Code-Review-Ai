import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import UnauthorizedError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decrypt_token,
    encrypt_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)
from app.models.session import UserSession
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.base import BaseService
from app.services.github_oauth import GitHubOAuthService


class AuthService(BaseService[UserRepository]):
    def __init__(self, repository: UserRepository, db: AsyncSession):
        super().__init__(repository)
        self.db = db

    async def register_user(self, user_in: UserCreate) -> User:
        """Register a new user after validating uniqueness."""
        existing = await self.repository.get_by_email(user_in.email)
        if existing:
            raise ValidationError(f"Email '{user_in.email}' is already registered.")

        existing_user = await self.repository.get_by_username(user_in.username)
        if existing_user:
            raise ValidationError(f"Username '{user_in.username}' is already taken.")

        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = get_password_hash(user_in.password)
        user_data["role"] = "DEVELOPER"
        
        return await self.repository.create(user_data)

    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user credentials and return user model instance."""
        user = await self.repository.get_by_email(email)
        if not user or not user.hashed_password:
            raise UnauthorizedError("Invalid email or password.")
        
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password.")
            
        if not user.is_active:
            raise UnauthorizedError("User account is inactive.")

        return user

    async def create_session_and_tokens(
        self, user: User, user_agent: Optional[str] = None, ip_address: Optional[str] = None
    ) -> Tuple[str, str, int]:
        """
        Create a new persistent UserSession in DB and generate Access + Refresh token pair.
        Returns: (access_token, refresh_token, expires_in_seconds)
        """
        raw_refresh_token = create_refresh_token()
        token_hash = hash_refresh_token(raw_refresh_token)
        
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        session = UserSession(
            user_id=user.id,
            refresh_token_hash=token_hash,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=expires_at,
            is_revoked=False,
        )
        self.db.add(session)
        await self.db.flush()

        access_token = create_access_token(subject=str(user.id), role=user.role)
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        return access_token, raw_refresh_token, expires_in

    async def refresh_session_tokens(
        self, refresh_token_str: str, user_agent: Optional[str] = None, ip_address: Optional[str] = None
    ) -> Tuple[str, str, int, User]:
        """
        Validate refresh token, rotate refresh token, and issue new Access + Refresh token pair.
        """
        token_hash = hash_refresh_token(refresh_token_str)
        
        statement = select(UserSession).where(UserSession.refresh_token_hash == token_hash)
        result = await self.db.execute(statement)
        session = result.scalars().first()

        if not session or not session.is_valid:
            raise UnauthorizedError("Invalid or expired refresh token session.")

        # Revoke old session (Refresh Token Rotation)
        session.is_revoked = True
        self.db.add(session)

        # Get User
        user = await self.repository.get_by_id(session.user_id)
        if not user or not user.is_active:
            raise UnauthorizedError("User associated with session is inactive or removed.")

        # Create new session & issue fresh tokens
        new_access, new_refresh, expires_in = await self.create_session_and_tokens(
            user, user_agent=user_agent, ip_address=ip_address
        )
        return new_access, new_refresh, expires_in, user

    async def logout_session(self, refresh_token_str: str) -> bool:
        """Revoke user session upon logout."""
        if not refresh_token_str:
            return False
        token_hash = hash_refresh_token(refresh_token_str)
        statement = select(UserSession).where(UserSession.refresh_token_hash == token_hash)
        result = await self.db.execute(statement)
        session = result.scalars().first()
        if session:
            session.is_revoked = True
            self.db.add(session)
            await self.db.flush()
            return True
        return False

    async def authenticate_github_user(
        self, code: str, user_agent: Optional[str] = None, ip_address: Optional[str] = None
    ) -> Tuple[User, str, str, int]:
        """
        Complete GitHub OAuth authentication flow: exchange code, fetch profile, upsert user,
        encrypt GitHub token, and issue platform access & refresh tokens.
        """
        github_oauth = GitHubOAuthService()
        github_token = await github_oauth.exchange_code_for_token(code)
        profile = await github_oauth.fetch_user_profile(github_token)

        github_user_id = profile["id"]
        email = profile.get("email") or f"{profile['login']}@users.noreply.github.com"
        username = profile["login"]
        full_name = profile.get("name") or username
        avatar_url = profile.get("avatar_url")

        # Encrypt sensitive GitHub token for storage
        encrypted_token = encrypt_token(github_token)

        # Find existing user by github_user_id or email
        statement = select(User).where(User.github_user_id == github_user_id)
        result = await self.db.execute(statement)
        user = result.scalars().first()

        if not user:
            user = await self.repository.get_by_email(email)

        if user:
            # Update user GitHub data & encrypted access token
            user.github_user_id = github_user_id
            user.encrypted_github_token = encrypted_token
            user.avatar_url = avatar_url
            user.full_name = full_name
            self.db.add(user)
        else:
            # Create new user
            user_data = {
                "email": email,
                "username": username,
                "full_name": full_name,
                "avatar_url": avatar_url,
                "github_user_id": github_user_id,
                "encrypted_github_token": encrypted_token,
                "role": "DEVELOPER",
                "is_active": True,
            }
            user = await self.repository.create(user_data)

        await self.db.flush()

        # Issue tokens & create active session
        access_token, refresh_token, expires_in = await self.create_session_and_tokens(
            user, user_agent=user_agent, ip_address=ip_address
        )
        return user, access_token, refresh_token, expires_in
