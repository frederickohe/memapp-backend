from pydantic import BaseModel, Field


class ResetPassNoAuth(BaseModel):
    """Complete a forgot-password reset after OTP verification."""

    reset_token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=100)
