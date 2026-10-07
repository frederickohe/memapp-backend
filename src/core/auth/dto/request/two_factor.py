from pydantic import BaseModel, Field
from typing import Optional


class TwoFactorConfirmRequest(BaseModel):
    otp: str = Field(..., min_length=5, max_length=5)
    channel: Optional[str] = None


class TwoFactorSignInRequest(BaseModel):
    challenge_token: str = Field(..., min_length=10)
    otp: str = Field(..., min_length=5, max_length=5)


class TwoFactorResendRequest(BaseModel):
    challenge_token: str = Field(..., min_length=10)
