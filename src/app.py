from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import exceptions
from routes import base_routes
from core.auth.controller.authcontroller import auth_routes
from core.user.controller.usercontroller import user_routes
from core.cloudstorage.controller.storagecontoller import storage_routes
from core.notification.controller.notificationcontroller import notification_routes
from core.otp.controller.otpcontroller import otp_routes
from core.news.controller.newscontroller import news_routes
from core.forms.controller.formcontroller import form_routes
from core.programs.controller.programcontroller import program_routes
from core.rbac.controller.role_controller import role_routes
from core.rbac.controller.admin_user_controller import admin_user_routes
from core.rbac.service.permission_service import PermissionService

from utilities.dbconfig import Base, engine, SessionLocal
from config import settings
from utilities.exceptions import DatabaseValidationError
from fastapi.exceptions import RequestValidationError
from sqlalchemy import inspect

from loguru import logger
import logging
from contextlib import asynccontextmanager


# Initialize FastAPI with lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("[APP_STARTUP] Application starting...")
    db = SessionLocal()
    try:
        PermissionService(db).ensure_seed_data()
        logger.info("[APP_STARTUP] RBAC seed data ensured")
    except Exception as exc:
        logger.warning(f"[APP_STARTUP] RBAC seed skipped: {exc}")
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("[APP_SHUTDOWN] Application shutting down...")


app = FastAPI(
    title=settings.SERVICE_NAME,
    version="1.0",
    description="""**Ymca App API** An AI focused app infrastructure deployed with python.

    Default Endpoints:
    - Authentication
    - File and Document Management
    - Message and Task Queuing
    - Notifications
    """,
    contact={
        "name": "API Support",
        "url": "http://support@ymca.com",
        "email": "mail@ymca.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# print("Initializing database tables...")
# Base.metadata.create_all(bind=engine)
# print("Database tables initialized successfully.")

# -----------------------------------------------------------
# Middleware (CORS)
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # JWT auth uses Authorization headers, not cookies. Credentials mode must stay
    # off when allow_origins is "*" — otherwise browsers reject responses that
    # combine Allow-Origin: * with Allow-Credentials: true (Failed to fetch).
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers

app.add_exception_handler(DatabaseValidationError, exceptions.database_validation_exception_handler)
app.add_exception_handler(RequestValidationError, exceptions.validation_exception_handler)

# Routes Registration

app.include_router(base_routes, prefix="/api/v1", tags=["Base Routes"])
app.include_router(storage_routes, prefix="/api/v1/storage", tags=["Storage Routes"])
app.include_router(auth_routes, prefix="/api/v1/auth", tags=["Auth Routes"])
app.include_router(user_routes, prefix="/api/v1/user", tags=["User Routes"])
app.include_router(notification_routes, prefix="/api/v1/notification", tags=["Notification Routes"])
app.include_router(otp_routes, prefix="/api/v1/otp", tags=["OTP Routes"])
app.include_router(news_routes, prefix="/api/v1/news", tags=["News Routes"])
app.include_router(form_routes, prefix="/api/v1/form", tags=["Forms Routes"])
app.include_router(program_routes, prefix="/api/v1/program", tags=["Programs Routes"])
app.include_router(role_routes, prefix="/api/v1/admin", tags=["Admin RBAC"])
app.include_router(admin_user_routes, prefix="/api/v1/admin", tags=["Admin Users"])

# JWT Authentication Settings

class JWTSettings(BaseSettings):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_algorithm: str = settings.ALGORITHM
    authjwt_access_token_expires: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds
    authjwt_refresh_token_expires: int = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60  # in seconds


@AuthJWT.load_config
def get_config():
    return JWTSettings()