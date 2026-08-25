from pydantic import BaseModel, EmailStr, Field, validator


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)

    @validator("email", pre=True)
    def normalize_email(cls, value):
        if value is None:
            return value
        return str(value).strip().lower()
