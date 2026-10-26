from pydantic import BaseModel, Field


class ForgotPasswordRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=32)


class ForgotPasswordVerifyRequest(BaseModel):
    phone: str = Field(..., min_length=7, max_length=32)
    otp: str = Field(..., min_length=5, max_length=5)


class ForgotPasswordResetRequest(BaseModel):
    reset_token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=100)
