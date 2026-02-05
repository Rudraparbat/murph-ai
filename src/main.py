"""
FastAPI Application Initialization

This script sets up the FastAPI app, configures settings,
and imports required modules (models, views, and routes).
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.user_config import auth_backend , fastapi_users
from src.models.schemas.schema import UserRead , UserCreate , UserUpdate

SECRET_KEY = os.urandom(32)

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    expose_headers=["*"],
    max_age=600,
)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Langraph API!"}