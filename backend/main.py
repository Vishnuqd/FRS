from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.auth import router as auth_router
from backend.bmi import router as bmi_router
from backend.recipes import router as recipes_router

app = FastAPI(
    title="Food API",
    description="API for Food Finder Application",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ Fix CORS Issue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],  # Allow both frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(auth_router, prefix="/auth")
app.include_router(bmi_router, prefix="/bmi")
app.include_router(recipes_router, prefix="/recipes")
