from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.token import LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> dict:
    """
    Realiza o login do usuário e retorna um token JWT.

    - **email**: email cadastrado pelo admin
    - **senha**: senha definida na criação da conta
    """
    return auth_service.login(db, data.email, data.senha)
