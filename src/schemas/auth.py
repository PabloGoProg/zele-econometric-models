"""Schemas de autenticación y gestión de usuarios."""

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Solicitud de registro de usuario."""

    name: str = Field(..., min_length=2, max_length=100, description="Nombre del usuario")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña del usuario")


class UserLoginRequest(BaseModel):
    """Solicitud de inicio de sesión."""

    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class TokenResponse(BaseModel):
    """Respuesta con el token de autenticación."""

    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")


class UserResponse(BaseModel):
    """Respuesta con información del usuario."""

    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}
