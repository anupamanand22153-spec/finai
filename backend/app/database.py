import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# 1. Load credentials from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Create the Async Engine (The Connection Manager)
# echo=True prints every raw SQL command directly into the terminal
engine = create_async_engine(DATABASE_URL, echo=True)

# 3. Create Session Factory (Dispenses isolated database connections)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 4. Declarative Base (Parent blueprint for our database tables)
Base = declarative_base()


# 5. Dependency for FastAPI endpoints
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()