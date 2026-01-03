import pprint

import httpx

from core.config import settings
from typing import Dict, Any, Optional

BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "Authorization": f"Bearer {settings.TMDB_API_KEY}",
    "accept": "application/json"
}

params = {'language': 'ru-RU'}


async def fetch_tmdb_data(endpoint: str, params: dict = None) -> Optional[Dict[str, Any]]:
    """
    Асинхронно выполняет GET-запрос к TMDb.
    """
    url = f"{BASE_URL}{endpoint}"

    # Создаем копию базовых параметров, чтобы не мутировать глобальную переменную
    # и подмешиваем новые параметры, если они переданы
    request_params = {'language': 'ru-RU'}
    if params:
        request_params.update(params)

    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
        try:
            # Используем request_params (базовые + дополнительные)
            response = await client.get(url, params=request_params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Выводим статус код и часть ответа для отладки
            print(f"[{e.response.status_code}] HTTP Error for {endpoint}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during fetch for {endpoint}: {e}")
            return None


async def fetch_popular_movie_ids(page: int = 1):
    """Получает список популярных фильмов с TMDB."""
    url = f"{BASE_URL}/movie/popular"
    params = {'language': 'ru-RU',
              'page': page,}
    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data


