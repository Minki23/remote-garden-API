from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeMeta
from datetime import datetime

T = TypeVar("T", bound=DeclarativeMeta)


class SuperRepo(Generic[T]):
    """
    Generic asynchronous repository for SQLAlchemy models.

    Provides basic CRUD operations for any declarative SQLAlchemy model.
    """

    def __init__(self, db: AsyncSession, model: Type[T]):
        """
        Initialize repository.

        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session.
        model : Type[T]
            SQLAlchemy model class for which the repo is created.
        """
        self.db = db
        self.model = model

    async def get_by_id(self, obj_id: UUID) -> Optional[T]:
        """Fetch a single object by its UUID primary key."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[T]:
        """Fetch all objects of the model."""
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, **kwargs) -> T:
        """
        Create and persist a new object.

        Automatically sets `created_at` and `updated_at` if present in the model.
        """
        obj = self.model(**kwargs)
        self.db.add(obj)

        if hasattr(obj, "updated_at"):
            setattr(obj, "updated_at", datetime.utcnow())
        if hasattr(obj, "created_at"):
            setattr(obj, "created_at", datetime.utcnow())

        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj_id: UUID, **kwargs) -> Optional[T]:
        """
        Update fields of an existing object.

        Only updates fields that exist on the model and skips `None` values.
        """
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
        """Delete an object by UUID. Returns True if deleted, False if not found."""
        obj = await self.get_by_id(obj_id)
        if not obj:
            return False

        await self.db.delete(obj)
        await self.db.commit()
        return True
