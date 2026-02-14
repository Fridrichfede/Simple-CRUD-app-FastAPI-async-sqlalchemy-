from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine #Async extentions for sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase #Tools for creating ORM
from sqlalchemy import String, Integer, Boolean, text, DateTime, select
from fastapi import FastAPI, HTTPException
from config import settings
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

class Base(DeclarativeBase):
    pass

async_engine = create_async_engine(url=settings.get_async_engine, echo=True)

class User(Base):
    __tablename__ = 'users'
    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email : Mapped[str] = mapped_column(String(64), unique=True)
    hashed_password : Mapped[str] = mapped_column(String(32))
    is_active : Mapped[bool] = mapped_column(Boolean)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True))

async def reset_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await reset_tables()
    yield
    print('app shutdown')

app = FastAPI(lifespan=lifespan)

asyn_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def execute_smth():
    async with asyn_session() as session:
        sql_response = (await session.execute(text('SELECT 1;'))).scalar()
        print(sql_response)

class UserCreate(BaseModel):
    email : str = Field(..., min_length=10, max_length=64)
    hashed_password : str = Field(..., min_length=8, max_length=32)
    is_active : bool 
    created_at : datetime 

    @field_validator('created_at')
    def check_datetime(cls, date: datetime):
        now = datetime.now(timezone.utc)
        if date.tzinfo == None:
           date = date.replace(timezone.utc)
        if date > now:
             raise ValueError('Invalid datetime provided')
        return date
        
class UserUpdate(BaseModel):
    email : Optional[str] = Field(None, min_length=10, max_length=64)
    hashed_password : Optional[str] = Field(None, min_length=8, max_length=32)
    is_active : Optional[bool] = Field(None)
    created_at : Optional[datetime] = Field(None)

    @field_validator('created_at')
    def check_date(cls, date: datetime):
        now = datetime.now(timezone.utc)
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        if date > now:
            raise ValueError('Invalid Date Provided')
        return date


@app.post('/users')
async def post_user(user:UserCreate):
    async with asyn_session() as session:
        new_user = User(
            email= user.email,
            hashed_password= user.hashed_password,
            is_active= user.is_active,
            created_at=user.created_at
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    

@app.get('/users')
async def get_users():
    async with asyn_session() as session:
        users = (await session.execute(select(User))).scalars().all()
        return users
        
@app.get('/users/{id}')
async def get_user(user_id: int):
    async with asyn_session() as session:
        sql_response = await session.get(User, user_id)
        return sql_response


@app.patch('/users/{user_id}')
async def patch_users(user_id: int, user:UserUpdate):
    async with asyn_session() as session:
        user_db = await session.get(User, user_id)
        if not user_db:
            raise HTTPException(status_code=404, detail='User not found')
        
        for field, value in user.model_dump(exclude_unset=True).items():
            setattr(user_db, field, value)

        await session.commit()
        await session.refresh(user_db)
        return user_db
        
        
@app.delete('/users/{user_id}')
async def delete_user(user_id: int):
    async with asyn_session() as session:
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail='User not found')
        await session.delete(user)
        updated_db = await session.commit()
        return updated_db

    


