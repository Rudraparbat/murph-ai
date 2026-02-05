from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os 
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv('PG_DB_URL')

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_local = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session_local() as session:
        yield session

