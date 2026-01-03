from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User as UserModel, Movie, Review
from core.models.users import UserRole
from core.schemas import ReviewCreate
from fastapi import HTTPException


class ReviewsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(self, current_user: UserModel,
                            movie_id: int,
                            review_data: ReviewCreate):

        movie = await self.db.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Фильм не найден")

        existing_review = await self.db.scalar(select(Review).where(
            Review.user_id == current_user.id,
            Review.movie_id == movie.id))
        if existing_review:
            raise HTTPException(status_code=400, detail="Вы уже оставили отзыв к этому фильму")

        new_review = Review(movie_id=movie_id,
                            user_id=current_user.id,
                            **review_data.model_dump()
                            )
        try:
            self.db.add(new_review)
            await self.db.commit()
            await self.db.refresh(new_review, ["user"])
            return new_review
        except Exception:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Ошибка при сохранении отзыва")

    async def update_review(self, current_user: UserModel,
                            movie_id: int,
                            review_data: ReviewCreate):
        movie = await self.db.get(Movie, movie_id)
        if not movie:
            raise HTTPException(status_code=404, detail="Фильм не найден")
        existing_review = await self.db.scalar(select(Review).where(
            Review.user_id == current_user.id,
            Review.movie_id == movie.id))
        if not existing_review:
            raise HTTPException(status_code=400, detail="Вы ещё не оставили отзыв к этому фильму")
        existing_review.review_text = review_data.review_text
        existing_review.review_type = review_data.review_type
        await self.db.commit()
        await self.db.refresh(existing_review, ["user"])
        return existing_review

    async def delete_review(self, movie_id: int, current_user: UserModel, review_id: int = None):
        if review_id:
            existing_review = await self.db.get(Review, review_id)
        else:
            existing_review = await self.db.scalar(
                select(Review).where(
                    Review.user_id == current_user.id,
                    Review.movie_id == movie_id
                )
            )

        if not existing_review:
            raise HTTPException(status_code=404, detail="Отзыв не найден в базе")

        is_owner = existing_review.user_id == current_user.id
        is_admin = str(current_user.role) == "admin" or getattr(current_user.role, "value", "") == "admin"

        if not (is_owner or is_admin):
            raise HTTPException(status_code=403, detail="Недостаточно прав для удаления этого отзыва")

        await self.db.delete(existing_review)
        await self.db.commit()

        return {"message": "Отзыв успешно удалён"}

