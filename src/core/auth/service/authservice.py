from typing import Optional
from fastapi.responses import JSONResponse
import jwt
from passlib.context import CryptContext
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi import status
from datetime import datetime, timedelta, timezone
from core.auth.service.sessiondriver import SessionDriver
from core.exceptions.AuthException import InvalidCredentialsError, PermissionDeniedError
from core.exceptions.UserException import UserAlreadyExistsError
from core.user.model.User import User, UserType
from core.rbac.service.rbac_service import RbacService
from core.rbac.service.role_service import RoleService
from core.rbac.service.admin_user_service import AdminUserService
from core.otp.service.otpservice import OTPService
from utilities.phone import normalize_phone
import secrets
import string
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.session_driver = SessionDriver()
        self.otp_service = OTPService(db)

    def hash_password(self, password: str) -> str:
        """Hash a plain-text password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain-text password against a hashed one."""
        return pwd_context.verify(plain_password, hashed_password)

    def generate_user_id(self):
        """Generate a random user ID with alphanumeric characters."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for i in range(20))

    def generate_member_id(self) -> str:
        """Generate a unique public membership ID."""
        for _ in range(8):
            candidate = "YID" + "".join(secrets.choice(string.digits) for _ in range(10))
            exists = self.db.query(User).filter(User.member_id == candidate).first()
            if not exists:
                return candidate
        return "YID" + self.generate_user_id()[:10]

    def _build_token_claims(self, user: User) -> dict:
        claims = {"sub": user.email, "user_type": user.user_type}
        if user.role_id:
            claims["role_id"] = user.role_id
        if user.role:
            claims["role"] = user.role
        return claims

    def _member_summary(self, user: User) -> dict:
        return {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "phone_number": user.phone_number,
            "nationality": user.nationality,
            "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
            "gender": user.gender,
            "address": user.address,
            "membership_type": user.membership_type,
            "current_branch": user.current_branch,
            "member_id": user.member_id,
            "enabled": user.enabled,
            "user_type": user.user_type,
        }

    def _token_body(self, user: User, message: str = "Login successful") -> dict:
        claims = self._build_token_claims(user)
        access_token = self.session_driver.create_access_token(
            data=claims,
            expires_delta=timedelta(minutes=self.session_driver.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = self.session_driver.create_refresh_token(data=claims)
        self.session_driver.store_tokens(access_token, refresh_token)

        return {
            "status": message,
            "message": message,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.session_driver.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_type": user.user_type,
            "role": user.role,
            "role_id": user.role_id,
            "user_id": user.id,
            "user": self._member_summary(user),
        }

    def _issue_tokens(self, user: User, message: str = "Login successful") -> JSONResponse:
        return JSONResponse(status_code=200, content=self._token_body(user, message))

    def create_user(self, request: BaseModel):
        """Create a new member and return an authenticated session."""
        email = str(request.email).strip().lower()
        existing_user = (
            self.db.query(User).filter(func.lower(User.email) == email).first()
        )
        if existing_user:
            raise UserAlreadyExistsError(field="email")

        user_id = self.generate_user_id()
        phone = normalize_phone(request.phone_number) or None
        whatsapp = normalize_phone(request.whatsapp_number) or phone
        if whatsapp and len(whatsapp) > 20:
            whatsapp = whatsapp[:20]

        db_user = User(
            id=user_id,
            fullname=request.fullname,
            phone_number=phone,
            email=email,
            hashed_password=self.hash_password(request.password),
            profile_picture_url=request.profile_picture_url,
            nationality=request.nationality,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
            address=request.address,
            membership_type=request.membership_type,
            current_branch=request.current_branch,
            member_id=request.member_id or self.generate_member_id(),
            facebook_url=request.facebook_url,
            whatsapp_number=whatsapp,
            linkedin_url=request.linkedin_url,
            twitter_url=request.twitter_url,
            instagram_url=request.instagram_url,
            occupation=request.occupation,
            organization_workplace=request.organization_workplace,
            skills=request.skills or [],
            experiences=request.experiences or [],
            profile_sharing=bool(request.profile_sharing),
            in_app_notification=bool(request.in_app_notification),
            sms_notification=bool(request.sms_notification),
            user_type=UserType.MEMBER,
            enabled=True,
            created_at=request.created_at or datetime.now(timezone.utc),
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
        except IntegrityError as exc:
            self.db.rollback()
            detail = str(getattr(exc, "orig", exc)).lower()
            if "email" in detail:
                raise UserAlreadyExistsError(field="email")
            if "member_id" in detail:
                db_user.member_id = self.generate_member_id()
                try:
                    self.db.add(db_user)
                    self.db.commit()
                    self.db.refresh(db_user)
                except IntegrityError:
                    self.db.rollback()
                    raise HTTPException(
                        status_code=400,
                        detail="Could not create account. Please try again.",
                    )
            elif "fullname" in detail:
                db_user.fullname = f"{request.fullname} {user_id[-4:]}"
                try:
                    self.db.add(db_user)
                    self.db.commit()
                    self.db.refresh(db_user)
                except IntegrityError:
                    self.db.rollback()
                    raise HTTPException(
                        status_code=400,
                        detail="Could not create account. Please try again.",
                    )
            else:
                logger.error(f"Signup integrity error: {exc}")
                raise HTTPException(
                    status_code=400,
                    detail="Could not create account. Please try again.",
                )

        if phone:
            try:
                self.otp_service.send_otp_phone(phone)
            except Exception as exc:
                logger.warning(f"Signup OTP send skipped for {phone}: {exc}")

        return self._issue_tokens(db_user, "Account created successfully")
    
    def verify_and_enable_user(self, phone: str, otp: str):
        """Verify OTP and enable user account"""
        # Validate OTP
        is_valid = self.otp_service.validate_otp(phone=phone, otp=otp)
        
        if not is_valid:
            return {
                "success": False,
                "message": "Invalid or expired OTP"
            }
        
        # Find user by phone
        user = self.db.query(User).filter(User.phone_number == phone).first()
        
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Enable user account
        user.enabled = True
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        
        return {
            "success": True,
            "message": "Phone number verified successfully. Your account is now active.",
            "user_id": user.id
        }
           
    def authenticate_user(self, email: str, password: str):
        normalized_email = (email or "").strip().lower()
        db_user = (
            self.db.query(User)
            .filter(func.lower(User.email) == normalized_email)
            .first()
        )

        if not db_user:
            raise InvalidCredentialsError()

        if not self.verify_password(password, db_user.hashed_password):
            raise InvalidCredentialsError()

        if db_user.user_type == UserType.MEMBER and not db_user.enabled:
            db_user.enabled = True
            db_user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(db_user)

        return db_user

    def signin(self, user: BaseModel):
        """Login the user by generating a JWT token and returning tokens."""
        db_user = self.authenticate_user(user.email, user.password)
        return self._issue_tokens(db_user)

    def admin_signin(self, user: BaseModel):
        """Login an admin user; rejects accounts that are not admins."""
        db_user = self.authenticate_user(user.email, user.password)

        if db_user.user_type != UserType.ADMIN:
            raise PermissionDeniedError(detail="Admin credentials required")

        if not db_user.enabled:
            raise PermissionDeniedError(detail="Admin account is disabled")

        AdminUserService(self.db).record_login(db_user)
        return self._issue_tokens(db_user)

    def create_admin(self, request: BaseModel, created_by: Optional[User] = None):
        """Create a new admin user account."""
        role_service = RoleService(self.db)
        rbac = RbacService(self.db)

        existing_admin_count = (
            self.db.query(User).filter(User.user_type == UserType.ADMIN).count()
        )

        if existing_admin_count > 0:
            if not created_by or created_by.user_type != UserType.ADMIN:
                raise PermissionDeniedError(
                    detail="Only an existing admin can create new admin accounts"
                )
            if not rbac.can_create_admin(created_by):
                raise PermissionDeniedError(
                    detail="You do not have permission to create admin accounts"
                )

        if request.role_id:
            target_role = role_service.get_role_entity(request.role_id)
        else:
            target_role = role_service.get_role_by_name("super_admin")

        if not target_role or not target_role.is_active:
            raise HTTPException(status_code=400, detail="Invalid role selected")

        if existing_admin_count > 0 and created_by and not rbac.can_assign_role(
            created_by, target_role
        ):
            raise PermissionDeniedError(
                detail=f"You cannot assign the {target_role.name} role"
            )

        existing_user = (
            self.db.query(User)
            .filter(
                (User.email == request.email) | (User.fullname == request.fullname)
            )
            .first()
        )

        if existing_user:
            if existing_user.email == request.email:
                raise UserAlreadyExistsError(field="email")
            raise UserAlreadyExistsError(field="fullname")

        db_user = User(
            id=self.generate_user_id(),
            fullname=request.fullname,
            phone_number=request.phone_number,
            email=request.email,
            hashed_password=self.hash_password(request.password),
            profile_picture_url=request.profile_picture_url,
            user_type=UserType.ADMIN,
            role=target_role.name.upper(),
            role_id=target_role.id,
            assigned_region=getattr(request, "assigned_region", None),
            assigned_branch=getattr(request, "assigned_branch", None),
            enabled=True,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return {
            "message": "Admin account created successfully",
            "user_id": db_user.id,
            "email": db_user.email,
            "user_type": db_user.user_type,
            "role": db_user.role,
            "role_id": db_user.role_id,
        }

    def build_admin_response(self, user: User) -> dict:
        """Serialize an admin user for profile endpoints."""
        if user.user_type != UserType.ADMIN:
            raise PermissionDeniedError(detail="Admin access required")

        role_summary = None
        role = user.admin_role or RoleService(self.db).get_role_entity(user.role_id or "")
        if role:
            role_summary = {"id": role.id, "name": role.name}

        return {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "phone_number": user.phone_number,
            "user_type": user.user_type,
            "role": role_summary,
            "profile_picture_url": user.profile_picture_url,
            "enabled": user.enabled,
            "reset_required": user.reset_required,
            "status": user.status,
            "created_at": user.created_at,
            "assigned_region": user.assigned_region,
            "assigned_branch": user.assigned_branch,
        }

    def get_admin_profile(self, user: User):
        """Return the authenticated admin's profile."""
        return self.build_admin_response(user)

    def signout(self, token: str):
        try:
            # Decode without expiration check
            payload = jwt.decode(
                token, 
                self.session_driver.SECRET_KEY, 
                algorithms=[self.session_driver.ALGORITHM],
                options={"verify_exp": False}
            )
            email = payload.get("sub")
            
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Triple protection:
            # 1. Blacklist this specific token
            self.session_driver.blacklist_token(token)
            
            # 2. Remove token storage
            self.session_driver.remove_tokens(email)
            
            return JSONResponse(
                status_code=200,
                content={"message": "Logout successful"}
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            # Still attempt to blacklist
            self.session_driver.blacklist_token(token)
            raise HTTPException(status_code=500, detail="Logout processing error")

    def refresh_tokens(self, refresh_token: str):
        """Refresh access token using refresh token"""
        try:
            new_access_token = self.session_driver.refresh_access_token(refresh_token)
            
            return JSONResponse(
                status_code=200,
                content={
                    "access_token": new_access_token,
                    "token_type": "bearer",
                    "expires_in": self.session_driver.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                }
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        
    def signout_all(self, token: str):
        """Logout the user from all devices by invalidating all their tokens"""
        try:
            payload = jwt.decode(
                token, 
                self.session_driver.SECRET_KEY, 
                algorithms=[self.session_driver.ALGORITHM],
                options={"verify_exp": False}
            )
            email = payload.get("sub")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Triple protection:
            # 1. Blacklist this specific token
            self.session_driver.blacklist_token(token)
            
            # 2. Remove token storage
            self.session_driver.remove_tokens(email)
            
            return JSONResponse(
                status_code=200,
                content={"message": "Logged out from all devices"}
            )
        except jwt.PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def verify_account(self, email: str):
        """Verify user account using email or username"""
        try:
            db_user = self.db.query(User).filter(User.email == email).first()

            if not db_user:
                raise InvalidCredentialsError()
            
            return JSONResponse(
                status_code=200,
                content={"message": "Account verified successfully"}
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not valid or expired"
            )
            
    def reset_password(self, request: BaseModel):
        """Reset password using a valid reset token (authenticated version)"""
        try:
            # Verify the reset token
            payload = jwt.decode(
                request.reset_token,
                self.session_driver.SECRET_KEY,
                algorithms=[self.session_driver.ALGORITHM]
            )
            
            if payload.get("type") != "reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token type"
                )
                
            email = payload.get("sub")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token payload"
                )
            
            # Find user and update password
            db_user = self.db.query(User).filter(User.email == email).first()
            if not db_user:
                raise InvalidCredentialsError()
                
            db_user.hashed_password = self.hash_password(request.new_password)
            self.db.commit()
            
            # Invalidate all existing tokens
            self.session_driver.remove_tokens(email)
            
            return JSONResponse(
                status_code=200,
                content={"message": "Password reset successfully"}
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

    def reset_password_no_auth(self, request: BaseModel):
        """Reset password without authentication (for forgotten password flow)"""
        try:
            # Find user by email
            db_user = self.db.query(User).filter(User.email == request.email).first()
            if not db_user:
                # Don't reveal whether email exists for security
                return JSONResponse(
                    status_code=200,
                    content={"message": "If the email exists, password has been reset"}
                )
                
            # Update password
            db_user.hashed_password = self.hash_password(request.new_password)
            self.db.commit()
            
            # Invalidate all existing tokens
            self.session_driver.remove_tokens(request.email)
            
            return JSONResponse(
                status_code=200,
                content={"message": "If the email exists, password has been reset"}
            )
            
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error resetting password"
            )

    def generate_password_reset_token(self, email: str) -> str:
        """Generate a password reset token for the user"""
        try:
            # Verify user exists
            db_user = self.db.query(User).filter(User.email == email).first()
            if not db_user:
                # Don't reveal whether email exists
                return None
                
            # Create reset token that expires in 1 hour
            reset_data = {
                "sub": email,
                "type": "reset",
                "exp": datetime.now(timezone.utc) + timedelta(hours=1)
            }
            
            return jwt.encode(
                reset_data,
                self.session_driver.SECRET_KEY,
                algorithm=self.session_driver.ALGORITHM
            )
            
        except Exception as e:
            logger.error(f"Error generating reset token: {str(e)}")
            return None