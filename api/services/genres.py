from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.movies import Genre


class GenreService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_genres(self):
        result = (await self.db.scalars(select(Genre))).all()
        if not result:
            raise ValueError("Genre not found")
        return list(result)


