import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.artifacts import GeneratedTest
from app.models.pull_request import PullRequest
from app.schemas.test_generator_dto import (
    GeneratedTestItem,
    TestGenerationRequest,
    TestGeneratorResponse,
)
from app.services.test_generator.generator import AITestGeneratorEngine


class TestGeneratorService:
    """
    Service managing AI test generation, database persistence in GeneratedTest model,
    and formatted test file exports.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_and_save_test(
        self, request: TestGenerationRequest
    ) -> TestGeneratorResponse:
        """
        Generate test suite for given source code, persist snapshot to DB, and return response DTO.
        """
        # Validate PR if provided
        pr_id: uuid.UUID | None = request.pull_request_id
        if pr_id:
            pr_stmt = select(PullRequest).where(PullRequest.id == pr_id)
            pr_res = await self.db.execute(pr_stmt)
            if not pr_res.scalars().first():
                pr_id = None

        # Execute Engine Generation
        generated = AITestGeneratorEngine.generate_test_suite(
            target_file=request.target_file,
            code_content=request.code_content,
            test_framework=request.test_framework,
            test_category=request.test_category,
        )

        # Save to GeneratedTest table
        test_record = GeneratedTest(
            pull_request_id=pr_id,
            test_framework=generated["test_framework"],
            test_category=generated["test_category"],
            test_name=generated["test_name"],
            target_file=generated["target_file"],
            generated_code=generated["generated_code"],
            workflow_explanation=generated["workflow_explanation"],
            is_passing=True,
        )
        self.db.add(test_record)
        await self.db.flush()

        download_url = f"/api/v1/tests/download/{test_record.id}"

        return TestGeneratorResponse(
            test_id=test_record.id,
            test_framework=test_record.test_framework,
            test_category=test_record.test_category,
            test_name=test_record.test_name or "test_suite.py",
            target_file=test_record.target_file,
            generated_code=test_record.generated_code,
            workflow_explanation=test_record.workflow_explanation or "",
            download_url=download_url,
            is_passing=True,
        )

    async def get_test_by_id(self, test_id: uuid.UUID) -> GeneratedTest:
        """
        Retrieve a single generated test record by ID.
        """
        stmt = select(GeneratedTest).where(GeneratedTest.id == test_id)
        res = await self.db.execute(stmt)
        record = res.scalars().first()
        if not record:
            raise NotFoundError("GeneratedTest", test_id)
        return record

    async def get_pr_generated_tests(self, pr_id: uuid.UUID) -> list[GeneratedTestItem]:
        """
        Fetch all generated test records associated with a Pull Request.
        """
        stmt = select(GeneratedTest).where(GeneratedTest.pull_request_id == pr_id).order_by(GeneratedTest.created_at.desc())
        res = await self.db.execute(stmt)
        records = list(res.scalars().all())
        return [GeneratedTestItem.model_validate(r) for r in records]
