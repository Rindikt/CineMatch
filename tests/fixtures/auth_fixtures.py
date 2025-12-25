import pytest
from httpx import AsyncClient, ASGITransport
from core.db import get_db, Base
from core.auth import create_access_token
from core.models.users import User, UserRole
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from api.main import app

# Настройки БД переезжают сюда или остаются в базовом conftest
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False)

import pytest_asyncio

@pytest.fixture(scope="session", autouse=True)
async def cleanup_engine():
    yield
    await engine.dispose()


@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    from core.db import get_db
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session):
    user = User(email="test@test.com", nickname="tester", hashed_password="testpassword", is_active=True)
    db_session.add(user)
    await db_session.commit()
    return user

@pytest.fixture
async def test_admin(db_session):
    admin = User(email="admin@test.com",
                 nickname="admin_tester",
                 hashed_password="test_admin_password",
                 role=UserRole.admin,
                 is_active=True)
    db_session.add(admin)
    await db_session.commit()
    return admin

@pytest.fixture
async def admin_client(client, test_admin):
    token = create_access_token({"sub": test_admin.email, "id": test_admin.id})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture
async def auth_client(client, test_user):
    token = create_access_token({"sub": test_user.email, "id": test_user.id})
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client