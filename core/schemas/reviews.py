from pydantic import BaseModel, field_validator, Field, AliasPath
from datetime import datetime

from core.models.review import ReviewType


class ReviewCreate(BaseModel):
    review_text: str
    review_type: ReviewType # Используем твой Enum

class ReviewRead(ReviewCreate):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime
    user_email: str = Field(validation_alias=AliasPath("user", "email"))
    user_nickname: str = Field(validation_alias=AliasPath("user", "nickname"))

    class Config:
        from_attributes = True