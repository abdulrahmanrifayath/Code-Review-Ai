import uuid
from datetime import datetime, timezone
from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.core.security import decrypt_token
from app.models.pull_request import ChangedFile, Commit, PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.services.github_api import GitHubAPIService


class GitHubSyncService:
    """
    Orchestrates synchronization of Repositories, Pull Requests, Commits, and Changed Files
    from GitHub REST API into PostgreSQL ORM models.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_api_service(self, user: User) -> GitHubAPIService:
        """Decrypt user's stored GitHub access token and initialize API client."""
        if not user.encrypted_github_token:
            raise ValidationError("GitHub account is not connected. Please login with GitHub first.")
        plain_token = decrypt_token(user.encrypted_github_token)
        if not plain_token:
            raise ValidationError("Failed to decrypt GitHub access token.")
        return GitHubAPIService(plain_token)

    async def sync_repositories_for_user(self, user: User) -> List[Repository]:
        """
        Synchronize all accessible GitHub repositories into database.
        """
        api = self._get_api_service(user)
        repos_data = await api.get_user_repositories()
        synced_repos: List[Repository] = []

        for r_data in repos_data:
            github_repo_id = r_data["id"]
            full_name = r_data["full_name"]
            owner_login = r_data["owner"]["login"]
            name = r_data["name"]
            default_branch = r_data.get("default_branch", "main")
            is_private = r_data.get("private", True)
            language = r_data.get("language")

            # Check existing repository in DB
            stmt = select(Repository).where(Repository.github_repo_id == github_repo_id)
            res = await self.db.execute(stmt)
            repo = res.scalars().first()

            if repo:
                repo.name = name
                repo.full_name = full_name
                repo.owner_login = owner_login
                repo.default_branch = default_branch
                repo.is_private = is_private
                repo.language = language
                repo.is_active = True
                self.db.add(repo)
            else:
                repo = Repository(
                    github_repo_id=github_repo_id,
                    name=name,
                    full_name=full_name,
                    owner_login=owner_login,
                    default_branch=default_branch,
                    is_private=is_private,
                    language=language,
                    is_active=True,
                )
                self.db.add(repo)
            
            synced_repos.append(repo)

        await self.db.flush()
        return synced_repos

    async def sync_pull_requests_for_repo(self, user: User, repo_id: uuid.UUID) -> Tuple[Repository, List[PullRequest]]:
        """
        Synchronize Pull Requests, Commits, and Changed Files for a specific Repository.
        """
        stmt = select(Repository).where(Repository.id == repo_id)
        res = await self.db.execute(stmt)
        repo = res.scalars().first()
        if not repo:
            raise NotFoundError("Repository", repo_id)

        api = self._get_api_service(user)
        prs_data = await api.get_repository_pull_requests(repo.owner_login, repo.name)
        synced_prs: List[PullRequest] = []

        for pr_item in prs_data:
            pr_number = pr_item["number"]
            title = pr_item.get("title", "")
            body = pr_item.get("body", "")
            state = pr_item.get("state", "open")
            head_branch = pr_item["head"]["ref"]
            base_branch = pr_item["base"]["ref"]
            head_sha = pr_item["head"]["sha"]
            author_login = pr_item["user"]["login"]
            html_url = pr_item.get("html_url")

            # Check existing PR in DB
            pr_stmt = select(PullRequest).where(
                PullRequest.repository_id == repo.id, PullRequest.pr_number == pr_number
            )
            pr_res = await self.db.execute(pr_stmt)
            pr = pr_res.scalars().first()

            if pr:
                pr.title = title
                pr.body = body
                pr.state = state
                pr.head_branch = head_branch
                pr.base_branch = base_branch
                pr.head_sha = head_sha
                pr.author_login = author_login
                pr.html_url = html_url
                self.db.add(pr)
            else:
                pr = PullRequest(
                    repository_id=repo.id,
                    pr_number=pr_number,
                    title=title,
                    body=body,
                    state=state,
                    head_branch=head_branch,
                    base_branch=base_branch,
                    head_sha=head_sha,
                    author_login=author_login,
                    html_url=html_url,
                )
                self.db.add(pr)

            await self.db.flush()

            # Sync Commits for PR
            try:
                commits_data = await api.get_pull_request_commits(repo.owner_login, repo.name, pr_number)
                for c_item in commits_data:
                    sha = c_item["sha"]
                    commit_info = c_item.get("commit", {})
                    author_data = commit_info.get("author", {})
                    msg = commit_info.get("message", "")

                    c_stmt = select(Commit).where(Commit.pull_request_id == pr.id, Commit.commit_sha == sha)
                    c_res = await self.db.execute(c_stmt)
                    if not c_res.scalars().first():
                        commit_obj = Commit(
                            pull_request_id=pr.id,
                            commit_sha=sha,
                            author_name=author_data.get("name"),
                            author_email=author_data.get("email"),
                            message=msg,
                        )
                        self.db.add(commit_obj)
            except Exception:
                pass  # Soft failure for commits sync

            # Sync Changed Files for PR
            try:
                files_data = await api.get_pull_request_files(repo.owner_login, repo.name, pr_number)
                total_additions = 0
                total_deletions = 0
                for f_item in files_data:
                    fname = f_item["filename"]
                    fstatus = f_item.get("status", "modified")
                    adds = f_item.get("additions", 0)
                    dels = f_item.get("deletions", 0)
                    patch = f_item.get("patch")
                    raw_url = f_item.get("raw_url")

                    total_additions += adds
                    total_deletions += dels

                    f_stmt = select(ChangedFile).where(ChangedFile.pull_request_id == pr.id, ChangedFile.filename == fname)
                    f_res = await self.db.execute(f_stmt)
                    file_obj = f_res.scalars().first()

                    if file_obj:
                        file_obj.status = fstatus
                        file_obj.additions = adds
                        file_obj.deletions = dels
                        file_obj.patch = patch
                        file_obj.raw_url = raw_url
                        self.db.add(file_obj)
                    else:
                        file_obj = ChangedFile(
                            pull_request_id=pr.id,
                            filename=fname,
                            status=fstatus,
                            additions=adds,
                            deletions=dels,
                            patch=patch,
                            raw_url=raw_url,
                        )
                        self.db.add(file_obj)

                pr.additions = total_additions
                pr.deletions = total_deletions
                pr.changed_files_count = len(files_data)
                self.db.add(pr)
            except Exception:
                pass  # Soft failure for files sync

            synced_prs.append(pr)

        await self.db.flush()
        return repo, synced_prs
