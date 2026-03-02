"""Schemas for authentication and user management."""

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration.

    Attributes:
        name: Name of the user.
        email: Email address of the user.
        password: Password of the user.
    """

    name: str = Field(
        ..., min_length=2, max_length=100, description="Nombre del usuario"
    )
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(
        ..., min_length=6, max_length=128, description="Contraseña del usuario"
    )


class UserLoginRequest(BaseModel):
    """Schema for user login.

    Attributes:
        email: Email address of the user.
        password: Password of the user.
    """

    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class TokenResponse(BaseModel):
    """Schema for token response.

    Attributes:
        access_token: Access token for the user.
        token_type: Type of token.
    """

    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")


class UserResponse(BaseModel):
    """Schema for user response.
    
    Attributes:
        id: Unique identifier for the user.
        name: Name of the user.
        email: Email address of the user.
    """

    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}
