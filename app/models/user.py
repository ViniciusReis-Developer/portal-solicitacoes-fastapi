from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True  # permite retornar SQLAlchemy direto


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"