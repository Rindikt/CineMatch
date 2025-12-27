from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routers.movies import router as movies_router
from api.routers.actors import router as actors_router
from api.routers.genres import router as genres_router
from api.routers.users import router as users_router
from api.routers.admin import router as admin_router

from api.routers.integrations import router as integration_router
app = FastAPI(
    title='CineMatch API'
)

app.include_router(movies_router)
app.include_router(actors_router)
app.include_router(genres_router)
app.include_router(integration_router)
app.include_router(users_router)
app.include_router(admin_router)

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {'message': 'Добро пожаловать в API CineMatch'}