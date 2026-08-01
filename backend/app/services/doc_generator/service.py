import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.artifacts import GeneratedDocumentation
from app.models.pull_request import PullRequest
from app.schemas.doc_generator_dto import (
    DocGenerationRequest,
    DocGeneratorResponse,
    GeneratedDocItem,
)
from app.services.doc_generator.generator import AIDocGeneratorEngine


class DocGeneratorService:
    """
    Service managing AI documentation generation, PostgreSQL persistence in GeneratedDocumentation model,
    and formatted export downloads.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_and_save_doc(
        self, request: DocGenerationRequest
    ) -> DocGeneratorResponse:
        """
        Generate documentation for given source code/file, persist snapshot to DB, and return response DTO.
        """
        pr_id: uuid.UUID | None = request.pull_request_id
        if pr_id:
            pr_stmt = select(PullRequest).where(PullRequest.id == pr_id)
            pr_res = await self.db.execute(pr_stmt)
            if not pr_res.scalars().first():
                pr_id = None

        # Execute Engine Generation
        generated = AIDocGeneratorEngine.generate_documentation(
            target_file=request.target_file,
            code_content=request.code_content,
            doc_type=request.doc_type,
        )

        # Save to GeneratedDocumentation table
        doc_record = GeneratedDocumentation(
            pull_request_id=pr_id,
            doc_type=generated["doc_type"],
            doc_title=generated["doc_title"],
            target_file=generated["target_file"],
            content=generated["content"],
        )
        self.db.add(doc_record)
        await self.db.flush()

        download_url = f"/api/v1/docs/download/{doc_record.id}"

        return DocGeneratorResponse(
            doc_id=doc_record.id,
            doc_type=doc_record.doc_type,
            doc_title=doc_record.doc_title or f"Documentation for {doc_record.target_file}",
            target_file=doc_record.target_file,
            content=doc_record.content,
            download_url=download_url,
        )

    async def get_doc_by_id(self, doc_id: uuid.UUID) -> GeneratedDocumentation:
        """
        Retrieve a single generated doc record by ID.
        """
        stmt = select(GeneratedDocumentation).where(GeneratedDocumentation.id == doc_id)
        res = await self.db.execute(stmt)
        record = res.scalars().first()
        if not record:
            raise NotFoundError("GeneratedDocumentation", doc_id)
        return record

    async def get_pr_generated_docs(self, pr_id: uuid.UUID) -> list[GeneratedDocItem]:
        """
        Fetch all generated doc records associated with a Pull Request.
        """
        stmt = select(GeneratedDocumentation).where(GeneratedDocumentation.pull_request_id == pr_id).order_by(GeneratedDocumentation.created_at.desc())
        res = await self.db.execute(stmt)
        records = list(res.scalars().all())
        return [GeneratedDocItem.model_validate(r) for r in records]
