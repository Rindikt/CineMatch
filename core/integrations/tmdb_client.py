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

async def fetch_tmdb_data(endpoint:str, dop_params: dict = None) -> Optional[Dict[str, Any]]:
    """
    Асинхронно выполняет GET-запрос к TMDb.
    """
    url = f"{BASE_URL}{endpoint}"
    if dop_params:
        params.update(dop_params)


    async with httpx.AsyncClient(headers=HEADERS, timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"[{e.response.status_code}] HTTP Error for {endpoint}: {e} - Response: {e.response.text[:100]}...")
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


