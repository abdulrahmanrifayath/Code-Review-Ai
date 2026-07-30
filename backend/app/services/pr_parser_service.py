import uuid
from typing import List, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.core.security import decrypt_token
from app.models.pull_request import ChangedFile, PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.schemas.parser import ParsedFileDiffResponse, ParsedPRSummaryResponse
from app.services.diff_parser import detect_language_from_filename, parse_unified_diff
from app.services.github_api import GitHubAPIService


class PullRequestParserService:
    """
    Service for downloading PR diff patches from GitHub, parsing unified diffs,
    detecting programming languages, extracting added/deleted lines, and storing
    parsed diff structures in PostgreSQL.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def parse_and_store_pull_request_diffs(
        self, user: User, repository_id: uuid.UUID, pr_number: int
    ) -> ParsedPRSummaryResponse:
        """
        Download, parse, and store diffs for a Pull Request.
        """
        # Fetch Repository
        repo_stmt = select(Repository).where(Repository.id == repository_id)
        repo_res = await self.db.execute(repo_stmt)
        repo = repo_res.scalars().first()
        if not repo:
            raise NotFoundError("Repository", repository_id)

        # Fetch PullRequest
        pr_stmt = select(PullRequest).where(
            PullRequest.repository_id == repository_id, PullRequest.pr_number == pr_number
        )
        pr_res = await self.db.execute(pr_stmt)
        pr = pr_res.scalars().first()
        if not pr:
            raise NotFoundError("PullRequest", pr_number)

        # Initialize GitHub API
        if not user.encrypted_github_token:
            raise ValidationError("GitHub account is not connected.")
        plain_token = decrypt_token(user.encrypted_github_token)
        api = GitHubAPIService(plain_token)

        # Download raw changed files & patches
        owner, repo_name = repo.owner_login, repo.name
        files_data = await api.get_pull_request_files(owner, repo_name, pr_number)

        parsed_file_responses: List[ParsedFileDiffResponse] = []
        languages_detected: Set[str] = set()
        total_additions = 0
        total_deletions = 0

        for f_data in files_data:
            filename = f_data["filename"]
            fstatus = f_data.get("status", "modified")
            additions = f_data.get("additions", 0)
            deletions = f_data.get("deletions", 0)
            patch = f_data.get("patch", "")
            raw_url = f_data.get("raw_url")

            total_additions += additions
            total_deletions += deletions

            # Detect programming language & parse unified diff
            language = detect_language_from_filename(filename)
            languages_detected.add(language)

            parsed_diff = parse_unified_diff(patch) if patch else {}

            # Check existing ChangedFile record in DB
            cf_stmt = select(ChangedFile).where(
                ChangedFile.pull_request_id == pr.id, ChangedFile.filename == filename
            )
            cf_res = await self.db.execute(cf_stmt)
            cf_obj = cf_res.scalars().first()

            if cf_obj:
                cf_obj.status = fstatus
                cf_obj.language = language
                cf_obj.additions = additions
                cf_obj.deletions = deletions
                cf_obj.patch = patch
                cf_obj.parsed_diff = parsed_diff
                cf_obj.raw_url = raw_url
                self.db.add(cf_obj)
            else:
                cf_obj = ChangedFile(
                    pull_request_id=pr.id,
                    filename=filename,
                    status=fstatus,
                    language=language,
                    additions=additions,
                    deletions=deletions,
                    patch=patch,
                    parsed_diff=parsed_diff,
                    raw_url=raw_url,
                )
                self.db.add(cf_obj)

            await self.db.flush()

            parsed_file_responses.append(
                ParsedFileDiffResponse(
                    id=cf_obj.id,
                    filename=filename,
                    status=fstatus,
                    language=language,
                    additions=additions,
                    deletions=deletions,
                    patch=patch,
                    parsed_diff=parsed_diff,
                )
            )

        # Update PullRequest stats
        pr.additions = total_additions
        pr.deletions = total_deletions
        pr.changed_files_count = len(files_data)
        self.db.add(pr)
        await self.db.flush()

        return ParsedPRSummaryResponse(
            repository_full_name=repo.full_name,
            pr_number=pr.pr_number,
            pr_title=pr.title,
            changed_files_count=len(files_data),
            total_additions=total_additions,
            total_deletions=total_deletions,
            languages_detected=sorted(list(languages_detected)),
            files=parsed_file_responses,
        )

    async def get_stored_pull_request_diffs(
        self, repository_id: uuid.UUID, pr_number: int
    ) -> ParsedPRSummaryResponse:
        """
        Retrieve previously parsed PR diffs from database.
        """
        repo_stmt = select(Repository).where(Repository.id == repository_id)
        repo_res = await self.db.execute(repo_stmt)
        repo = repo_res.scalars().first()
        if not repo:
            raise NotFoundError("Repository", repository_id)

        pr_stmt = select(PullRequest).where(
            PullRequest.repository_id == repository_id, PullRequest.pr_number == pr_number
        )
        pr_res = await self.db.execute(pr_stmt)
        pr = pr_res.scalars().first()
        if not pr:
            raise NotFoundError("PullRequest", pr_number)

        cf_stmt = select(ChangedFile).where(ChangedFile.pull_request_id == pr.id)
        cf_res = await self.db.execute(cf_stmt)
        changed_files = list(cf_res.scalars().all())

        parsed_file_responses: List[ParsedFileDiffResponse] = []
        languages_detected: Set[str] = set()

        for cf in changed_files:
            if cf.language:
                languages_detected.add(cf.language)
            parsed_file_responses.append(
                ParsedFileDiffResponse(
                    id=cf.id,
                    filename=cf.filename,
                    status=cf.status,
                    language=cf.language,
                    additions=cf.additions,
                    deletions=cf.deletions,
                    patch=cf.patch,
                    parsed_diff=cf.parsed_diff,
                )
            )

        return ParsedPRSummaryResponse(
            repository_full_name=repo.full_name,
            pr_number=pr.pr_number,
            pr_title=pr.title,
            changed_files_count=len(changed_files),
            total_additions=pr.additions,
            total_deletions=pr.deletions,
            languages_detected=sorted(list(languages_detected)),
            files=parsed_file_responses,
        )
