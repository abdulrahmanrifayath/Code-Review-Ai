
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repository import Repository
from app.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    def __init__(self, db: AsyncSession):
        super().__init__(Repository, db)

    async def get_by_full_name(self, full_name: str) -> Repository | None:
        statement = select(Repository).where(Repository.full_name == full_name)
        result = await self.db.execute(statement)
        return result.scalars().first()

    async def get_by_owner_id(self, owner_id: int) -> list[Repository]:
        statement = select(Repository).where(Repository.owner_id == owner_id)
        result = await self.db.execute(statement)
        return list(result.scalars().all())
