from pydantic import BaseModel, EmailStr, Field

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    captcha_token: str

    #Input for swagger
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user1@example.com",
                    "password": "password",
                    "captcha_token": "token"
                }
            ]
        }
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    captcha_token: str

    #Input for swagger
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user1@example.com",
                    "password": "password",
                    "captcha_token": "token"
                }
            ]
        }
    }

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    access_token: str
    email: str
    token_type: str
