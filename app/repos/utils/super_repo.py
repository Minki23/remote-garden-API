from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeMeta
from datetime import datetime

T = TypeVar("T", bound=DeclarativeMeta)


class SuperRepo(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def get_by_id(self, obj_id: UUID) -> Optional[T]:
        result = await self.db.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> List[T]:
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj_id: UUID, **kwargs) -> Optional[T]:
        obj = await self.get_by_id(obj_id)
        if not obj:
            return None

        for key, value in kwargs.items():
            if hasattr(obj, key) and value is not None:
                setattr(obj, key, value)

        if hasattr(obj, "updated_at"):
            setattr(obj, "updated_at", datetime.utcnow())

        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj_id: UUID) -> bool:
        obj = await self.get_by_id(obj_id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True
