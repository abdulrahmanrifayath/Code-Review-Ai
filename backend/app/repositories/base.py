import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic Base Repository implementing standard CRUD data access patterns.
    Supports UUID and integer primary key lookups.
    """
    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id_val: uuid.UUID | str | int) -> ModelType | None:
        if isinstance(id_val, str):
            try:
                id_val = uuid.UUID(id_val)
            except ValueError:
                pass
        statement = select(self.model).where(self.model.id == id_val, self.model.deleted_at.is_(None))
        result = await self.db.execute(statement)
        return result.scalars().first()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        statement = select(self.model).where(self.model.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return list(result.scalars().all())

    async def create(self, obj_in_data: dict) -> ModelType:
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, update_data: dict) -> ModelType:
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value is not None:
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def soft_delete(self, id_val: uuid.UUID | str | int) -> ModelType | None:
        obj = await self.get_by_id(id_val)
        if obj:
            obj.soft_delete()
            self.db.add(obj)
            await self.db.flush()
        return obj

    async def delete(self, id_val: uuid.UUID | str | int) -> ModelType | None:
        obj = await self.get_by_id(id_val)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return obj
