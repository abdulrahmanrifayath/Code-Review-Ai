import asyncio
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import httpx
from app.core.config import settings
from app.core.errors import AppException, ValidationError


class RateLimitExceededError(AppException):
    """Exception raised when GitHub API rate limit is exhausted."""
    def __init__(self, reset_timestamp: int):
        wait_seconds = max(0, reset_timestamp - int(time.time()))
        super().__init__(
            message=f"GitHub API rate limit exceeded. Resets in {wait_seconds} seconds.",
            status_code=429,
            details={"reset_timestamp": reset_timestamp, "wait_seconds": wait_seconds},
        )


class GitHubAPIService:
    """
    Resilient GitHub REST API client featuring rate-limit detection,
    exponential backoff retries, and automatic RFC 5988 pagination.
    """
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValidationError("GitHub access token is required for API operations.")
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": settings.PROJECT_NAME,
        }

    async def _execute_request_with_retry(
        self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[httpx.Response, Dict[str, str]]:
        """
        Execute HTTP request with exponential backoff retries (3 attempts) and rate-limit tracking.
        """
        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}{endpoint}"
        max_retries = 3
        backoff = 1.0  # seconds

        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(1, max_retries + 1):
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=self.headers,
                        params=params,
                        json=json_data,
                    )

                    # Inspect GitHub Rate Limit headers
                    remaining = response.headers.get("x-ratelimit-remaining")
                    reset_time = response.headers.get("x-ratelimit-reset")

                    if remaining is not None and int(remaining) == 0 and response.status_code == 403:
                        reset_ts = int(reset_time) if reset_time else int(time.time()) + 60
                        raise RateLimitExceededError(reset_ts)

                    # Transient server errors: 500, 502, 503, 504 -> retry
                    if response.status_code in (500, 502, 503, 504) and attempt < max_retries:
                        await asyncio.sleep(backoff)
                        backoff *= 2.0
                        continue

                    if response.status_code >= 400:
                        error_detail = response.json() if response.content else {}
                        raise ValidationError(
                            f"GitHub API Error [{response.status_code}]: {error_detail.get('message', response.text)}"
                        )

                    return response, response.headers

                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt == max_retries:
                        raise ValidationError(f"GitHub API connection failed after {max_retries} attempts: {str(exc)}")
                    await asyncio.sleep(backoff)
                    backoff *= 2.0

        raise ValidationError("GitHub API request failed.")

    async def fetch_paginated(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Fetch all pages using GitHub RFC 5988 Link header headers (<...>; rel="next").
        """
        all_items: List[Dict[str, Any]] = []
        current_endpoint: Optional[str] = endpoint
        current_params = params.copy() if params else {}
        current_params.setdefault("per_page", 100)
        page_count = 0

        while current_endpoint and page_count < max_pages:
            page_count += 1
            response, headers = await self._execute_request_with_retry(
                "GET", current_endpoint, params=current_params if page_count == 1 else None
            )
            items = response.json()
            if isinstance(items, list):
                all_items.extend(items)
            else:
                break

            # Parse Link header rel="next"
            link_header = headers.get("link") or headers.get("Link")
            next_url = None
            if link_header:
                links = link_header.split(",")
                for link in links:
                    if 'rel="next"' in link:
                        match = re.search(r'<(.*?)>', link)
                        if match:
                            next_url = match.group(1)
                            break
            current_endpoint = next_url

        return all_items

    async def get_user_repositories(self) -> List[Dict[str, Any]]:
        """Fetch all repositories accessible by the authenticated user."""
        return await self.fetch_paginated("/user/repos", params={"sort": "updated", "direction": "desc"})

    async def get_repository_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch metadata for a single repository."""
        response, _ = await self._execute_request_with_retry("GET", f"/repos/{owner}/{repo}")
        return response.json()

    async def get_repository_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch branch list for a repository."""
        return await self.fetch_paginated(f"/repos/{owner}/{repo}/branches")

    async def get_repository_pull_requests(
        self, owner: str, repo: str, state: str = "all"
    ) -> List[Dict[str, Any]]:
        """Fetch pull requests for a repository."""
        return await self.fetch_paginated(
            f"/repos/{owner}/{repo}/pulls", params={"state": state, "sort": "updated", "direction": "desc"}
        )

    async def get_pull_request_commits(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Fetch commits for a pull request."""
        return await self.fetch_paginated(f"/repos/{owner}/{repo}/pulls/{pr_number}/commits")

    async def get_pull_request_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Fetch modified files and diff patches for a pull request."""
        return await self.fetch_paginated(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
