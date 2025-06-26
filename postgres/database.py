from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import AsyncGenerator

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# URL de conexión a la base de datos PostgreSQL con asyncpg
DATABASE_URL = os.getenv("POSTGRES_URI", "postgresql+asyncpg://postgres:1234@localhost:5432/Orbcomm")

# Crear engine asíncrono
engine = create_async_engine(DATABASE_URL, echo=True)

# Crear SessionLocal para obtener sesiones async
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para modelos ORM
Base = declarative_base()

# Función para proveer sesión async en FastAPI con yield
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
