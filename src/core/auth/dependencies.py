import jwt
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import MissingTokenError
from sqlalchemy.orm import Session

from core.user.model.User import User, UserType
from utilities.dbconfig import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validate_token(authjwt: AuthJWT = Depends()):
    try:
        authjwt.jwt_required()
        return authjwt
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired. Please log in again.",
        )
    except MissingTokenError:
        raise HTTPException(
            status_code=401,
            detail="No token found. Please create an account and log in.",
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def get_current_user(
    authjwt: AuthJWT = Depends(validate_token),
    db: Session = Depends(get_db),
) -> User:
    email = authjwt.get_jwt_subject()
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def optional_admin_user(
    authjwt: AuthJWT = Depends(),
    db: Session = Depends(get_db),
) -> User | None:
    """Return the authenticated admin if a valid admin token is provided, else None."""
    try:
        authjwt.jwt_required(optional=True)
        email = authjwt.get_jwt_subject()
        if not email:
            return None
        user = db.query(User).filter(User.email == email).first()
        if user and user.user_type == UserType.ADMIN:
            return user
    except Exception:
        pass
    return None
