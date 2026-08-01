import secrets
from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import ValidationError


class GitHubOAuthService:
    """
    Service for executing GitHub OAuth 2.0 flow and API requests.
    """
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_API_URL = "https://api.github.com/user"

    def get_authorization_url(self) -> tuple[str, str]:
        """
        Generate GitHub OAuth authorization redirect URL and anti-CSRF state token.
        """
        client_id = settings.GITHUB_CLIENT_ID.strip() if settings.GITHUB_CLIENT_ID else ""
        if not client_id or client_id.lower() in ("your_github_client_id", "your_client_id"):
            raise ValidationError(
                "GitHub OAuth Client ID is not configured. "
                "Please set GITHUB_CLIENT_ID in your backend .env file or use email/password login."
            )

        state = secrets.token_hex(16)
        params = {
            "client_id": client_id,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "read:user user:email repo",
            "state": state,
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.AUTHORIZE_URL}?{query_string}"
        return url, state

    async def exchange_code_for_token(self, code: str) -> str:
        """
        Exchange OAuth authorization code for GitHub access token.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"},
                timeout=10.0,
            )

        if response.status_code != 200:
            raise ValidationError("Failed to exchange OAuth code with GitHub.")

        data = response.json()
        if "error" in data:
            raise ValidationError(f"GitHub OAuth error: {data.get('error_description', data['error'])}")

        access_token = data.get("access_token")
        if not access_token:
            raise ValidationError("No access_token returned by GitHub.")

        return access_token

    async def fetch_user_profile(self, github_access_token: str) -> dict[str, Any]:
        """
        Fetch authenticated user profile from GitHub REST API.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_API_URL,
                headers={
                    "Authorization": f"Bearer {github_access_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": settings.PROJECT_NAME,
                },
                timeout=10.0,
            )

        if response.status_code != 200:
            raise ValidationError("Failed to fetch user profile from GitHub.")

        profile = response.json()

        # If email is private, fetch primary email
        if not profile.get("email"):
            async with httpx.AsyncClient() as client:
                emails_res = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {github_access_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": settings.PROJECT_NAME,
                    },
                    timeout=10.0,
                )
                if emails_res.status_code == 200:
                    emails = emails_res.json()
                    primary_email = next((e["email"] for e in emails if e.get("primary")), None)
                    if primary_email:
                        profile["email"] = primary_email

        return profile
