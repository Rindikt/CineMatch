from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Универсальная схема для ответа с пагинацией."""
    total_items: int = Field(..., description="Общее количество элементов, подходящих под фильтр.")
    page: int = Field(..., description="Текущий номер страницы.")
    pages: int = Field(..., description="Общее количество страниц.")
    items: List[T] = Field(..., description="Список элементов на текущей странице.")