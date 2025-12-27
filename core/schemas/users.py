from pydantic import BaseModel, Field, ConfigDict, computed_field
from core.models.users import WatchStatus

from core.schemas import MovieProgressRead


class UserRegister(BaseModel):
    email: str = Field(description="Email пользователя")
    nickname: str = Field(description='Никнейм пользователя')
    password: str = Field(min_length= 8, description='Пароль (минимум 8 символов)')

class UserBase(BaseModel):
    email: str = Field(description="Email пользователя")
    nickname: str = Field(description='Никнейм пользователя')
    role: str = Field(description='Роль пользователя')
    is_active: bool

class UserProfileResponse(BaseModel):
    email: str = Field(description="Email пользователя")
    nickname: str = Field(description='Никнейм пользователя')
    role: str = Field(description='Роль пользователя')
    all_progress: list['MovieProgressRead'] = Field(
        validation_alias='movie_progress',
        exclude=True
    )

    @computed_field
    def planned(self)-> list[MovieProgressRead]:
        return [m for m in self.all_progress if m.status==WatchStatus.PLANNED]

    @computed_field
    def watching(self)-> list[MovieProgressRead]:
        return [m for m in self.all_progress if m.status == WatchStatus.WATCHING]

    @computed_field
    def completed(self)-> list[MovieProgressRead]:
        return [m for m in self.all_progress if m.status == WatchStatus.COMPLETED]

    @computed_field
    def dropped(self)-> list[MovieProgressRead]:
        return [m for m in self.all_progress if m.status == WatchStatus.DROPPED]

    model_config = ConfigDict(from_attributes=True)


