"""
FastAPI Application Initialization

This script sets up the FastAPI app, configures settings,
and imports required modules (models, views, and routes).
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {"message": "Welcome to the Langraph API!"}