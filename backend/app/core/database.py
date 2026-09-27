import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
from app.models.db import Base

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.storage.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    """Inicializa el esquema de SQLite si no existe."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Base de datos SQLite asíncrona inicializada.")
