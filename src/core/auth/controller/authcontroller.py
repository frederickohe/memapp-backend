from fastapi import APIRouter, Depends, Form
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from core.auth.dto.request.user_create import UserCreateRequest
from core.auth.dto.request.userlogin import UserLoginRequest
from core.auth.dto.request.admin_create import AdminCreateRequest
from core.auth.dto.request.resetpassword import ResetPasswordRequest
from core.auth.dto.request.resetpassnoauth import ResetPassNoAuth
from core.auth.dto.request.otp_verify import OTPVerifyRequest
from core.auth.dto.request.refresh_token import RefreshTokenRequest
from core.auth.dto.response.admin_response import AdminResponse
from core.auth.service.authservice import AuthService
from core.auth.dependencies import get_db, validate_token, require_admin, optional_admin_user
from core.user.model.User import User
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


auth_routes = APIRouter()


@auth_routes.post("/signup")
def signup(request: UserCreateRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)

    return auth_service.create_user(request)


@auth_routes.post("/signin")
def signin(user: UserLoginRequest, db: Session = Depends(get_db), authjwt: AuthJWT = Depends()):
    auth_service = AuthService(db)

    return auth_service.signin(user)


@auth_routes.post("/signout")
def signout(authjwt: AuthJWT = Depends(validate_token), db: Session = Depends(get_db)):
    token = authjwt._token
    auth_service = AuthService(db)

    return auth_service.signout(token)


@auth_routes.post("/verify-account")
async def verify_account(
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.verify_account(email)


@auth_routes.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    authjwt: AuthJWT = Depends(validate_token)
):
    auth_service = AuthService(db)
    return auth_service.reset_password(request)


@auth_routes.post("/no-auth/reset-password")
async def reset_password_no_auth(
    request: ResetPassNoAuth,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.reset_password_no_auth(request)


@auth_routes.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP and enable user account"""
    auth_service = AuthService(db)
    return auth_service.verify_and_enable_user(request.phone, request.otp)


# ============= ADMIN AUTH ROUTES =============

@auth_routes.post("/admin/signup")
def admin_signup(
    request: AdminCreateRequest,
    db: Session = Depends(get_db),
    created_by: User | None = Depends(optional_admin_user),
):
    """Create an admin account. First admin can bootstrap without auth; subsequent admins require an existing admin."""
    auth_service = AuthService(db)
    return auth_service.create_admin(request, created_by=created_by)


@auth_routes.post("/admin/signin")
def admin_signin(user: UserLoginRequest, db: Session = Depends(get_db)):
    """Sign in as an admin user."""
    auth_service = AuthService(db)
    return auth_service.admin_signin(user)


@auth_routes.get("/admin/me", response_model=AdminResponse)
def admin_me(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Get the currently authenticated admin's profile."""
    auth_service = AuthService(db)
    return auth_service.build_admin_response(admin)


@auth_routes.post("/admin/signout")
def admin_signout(authjwt: AuthJWT = Depends(validate_token), db: Session = Depends(get_db)):
    """Sign out the current admin session."""
    token = authjwt._token
    auth_service = AuthService(db)
    return auth_service.signout(token)


@auth_routes.post("/admin/refresh")
def admin_refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh an admin access token using a valid refresh token."""
    auth_service = AuthService(db)
    return auth_service.refresh_tokens(request.refresh_token)


@auth_routes.post("/refresh")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh an access token using a valid refresh token."""
    auth_service = AuthService(db)
    return auth_service.refresh_tokens(request.refresh_token)
