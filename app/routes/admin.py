from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service
from app.dependencies import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/usuarios", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> UserResponse:
    """
    Cria um novo usuário no sistema (admin, usuario ou fornecedor).
    Apenas o admin tem acesso a este endpoint (RN-01).
    """
    return user_service.create_user(db, data.nome, data.email, data.senha, data.role)


@router.get("/usuarios", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> List[UserResponse]:
    """
    Lista todos os usuários cadastrados no sistema.
    Visível apenas para o admin.
    """
    return user_service.list_users(db)


@router.patch("/usuarios/{user_id}/desativar", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> UserResponse:
    """
    Desativa a conta de um usuário pelo ID.
    O usuário desativado não consegue mais fazer login.
    """
    return user_service.deactivate_user(db, user_id)
