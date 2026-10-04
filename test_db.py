import asyncio
from backend.app.database import engine
from sqlalchemy import text


async def check_db_connection():
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT version();"))
            row = result.fetchone()
            print("\n" + "=" * 50)
            print(" Database connection successful!")
            print(f" Connected to: {row[0]}")
            print("=" * 50 + "\n")
    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ Database connection failed!")
        print(f"Error: {e}")
        print("=" * 50 + "\n")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_db_connection())