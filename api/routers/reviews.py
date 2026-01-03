from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.reviews import ReviewsService
from core.auth import get_current_user
from core.db import get_db
from core.models import User as UserModel
from core.schemas import ReviewCreate, ReviewRead

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)

@router.post("/{movie_id}/reviews", response_model=ReviewRead)
async def create_review(
        movie_id: int,
        review_data: ReviewCreate,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    reviews_service = ReviewsService(db)
    try:
        result =  await reviews_service.create_review(
            movie_id=movie_id,
            review_data=review_data,
            current_user=current_user)
        return result
    except Exception as e:
        raise e


@router.patch("/{movie_id}/reviews", response_model=ReviewRead)
async def update_review(
        movie_id: int,
        review_data: ReviewCreate,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    reviews_service = ReviewsService(db)
    try:
        result =  await reviews_service.update_review(movie_id=movie_id,
            review_data=review_data,
            current_user=current_user)
        return result
    except Exception as e:
        raise e

@router.delete("/{movie_id}/reviews")
async def delete_review(movie_id: int,
                        review_id: int = None,
                        current_user: UserModel = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db), ):
    reviews_service = ReviewsService(db)
    try:
        result = await reviews_service.delete_review(
            movie_id=movie_id,
            current_user=current_user,
            review_id=review_id)
        return result
    except Exception as e:
        raise e
