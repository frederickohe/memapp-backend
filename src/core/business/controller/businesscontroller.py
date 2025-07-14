from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from typing import List, Optional
import jwt
from pydantic import BaseModel
from core.auth.service.sessiondriver import SessionDriver, TokenData
from fastapi_jwt_auth import AuthJWT
from core.business.dto.request.businessupdate import BusinessUpdateRequest
from core.exceptions import *
from utilities.dbconfig import SessionLocal
from sqlalchemy.orm import Session
from core.user.model.User import User
from core.business.model.Business import Business
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# DTO Models
from core.user.dto.response.message_response import MessageResponse
from core.business.dto.response.business_response import BusinessResponse

from core.business.service.business_service import BusinessService
from fastapi_jwt_auth.exceptions import MissingTokenError

# Reuse the same token validation from user controller
from core.user.controller.usercontroller import validate_token

# Controller (Router)
business_routes = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@business_routes.get("/me", response_model=BusinessResponse)
def get_current_user_business(
    authjwt: AuthJWT = Depends(validate_token), 
    db: Session = Depends(get_db)
):
    current_user_email = authjwt.get_jwt_subject()
    business_service = BusinessService(db)
    return business_service.get_user_business(current_user_email)

@business_routes.put("/me", response_model=BusinessResponse)
def update_current_user_business(
    business_data: BusinessUpdateRequest,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    current_user_email = authjwt.get_jwt_subject()
    business_service = BusinessService(db)
    return business_service.update_user_business(current_user_email, business_data)

@business_routes.get("/user/{user_id}", response_model=BusinessResponse)
def get_business_by_user_id(
    user_id: str,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    # Add admin check here if needed
    business_service = BusinessService(db)
    return business_service.get_business_by_user_id(user_id)

@business_routes.put("/user/{user_id}", response_model=BusinessResponse)
def update_business_by_user_id(
    user_id: str,
    business_data: BusinessUpdateRequest,
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db)
):
    # Add admin check here if needed
    business_service = BusinessService(db)
    return business_service.update_business_by_user_id(user_id, business_data)