from sqlalchemy.orm import (
    declared_attr,
    DeclarativeBase
)

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)

from config import (
    DATABASE_URL,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
    POSTGRES_DB,
    DB_HOST,
    DB_PORT
)


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Base(PreBase, DeclarativeBase):
    pass


if not DATABASE_URL:
    DATABASE_URL = (
        f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}'
        f'@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}'
    )
engine = create_async_engine(DATABASE_URL, echo=True)
session = async_sessionmaker(engine, expire_on_commit=False)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
