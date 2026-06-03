"""Rutas de autenticación: registro, inicio de sesión y cierre de sesión."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core import settings
from src.database import get_db
from src.models.entities import User
from src.schemas.auth import (
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.services.auth_service import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

COOKIE_NAME = "access_token"
_IS_PRODUCTION = settings.NODE_ENV == "production"


def _set_auth_cookie(response: Response, token: str) -> None:
    """Setea la cookie httpOnly con el JWT."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="none" if _IS_PRODUCTION else "lax",
        secure=_IS_PRODUCTION,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registro de usuario",
    description="Crea una nueva cuenta de usuario y setea la cookie de sesión.",
)
def register(
    request: UserRegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    email = request.email.lower()
    existing = db.query(User).filter(func.lower(User.email) == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este correo electrónico",
        )

    user = User(
        name=request.name,
        email=email,
        password=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    _set_auth_cookie(response, token)
    return user


@router.post(
    "/login",
    response_model=UserResponse,
    summary="Inicio de sesión",
    description="Autentica al usuario y setea la cookie httpOnly con el JWT.",
)
def login(
    request: UserLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User).filter(func.lower(User.email) == request.email.lower()).first()
    )
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = create_access_token(data={"sub": str(user.id)})
    _set_auth_cookie(response, token)
    return user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cierre de sesión",
    description="Elimina la cookie de autenticación.",
)
def logout(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        samesite="none" if _IS_PRODUCTION else "lax",
        secure=_IS_PRODUCTION,
        path="/",
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Perfil de usuario",
    description="Retorna la información del usuario autenticado.",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
