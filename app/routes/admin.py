from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import require_role
from app.schemas.fornecedor import FornecedorCreate, FornecedorResponse
from app.schemas.pedido_compra import PedidoCompraSummary
from app.schemas.user import UserCreate, UserResponse
from app.services import fornecedor_service, pedido_service, user_service

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
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> List[UserResponse]:
    """
    Lista todos os usuários cadastrados no sistema.
    Quando q é informado, aplica busca manual por nome ou email.
    """
    return user_service.list_users(db, q)


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


@router.post("/fornecedores", response_model=FornecedorResponse)
def create_fornecedor(
    data: FornecedorCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> FornecedorResponse:
    """Cadastra um fornecedor com sua conta de acesso vinculada."""
    return fornecedor_service.create_fornecedor(db, data.nome, data.email, data.senha, data.cnpj)


@router.get("/fornecedores", response_model=List[FornecedorResponse])
def list_fornecedores(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> List[FornecedorResponse]:
    """Lista fornecedores com busca manual opcional por nome, email ou CNPJ."""
    return fornecedor_service.list_fornecedores(db, q)


@router.patch("/fornecedores/{fornecedor_id}/desativar", response_model=FornecedorResponse)
def deactivate_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> FornecedorResponse:
    """Desativa a conta de acesso do fornecedor informado."""
    return fornecedor_service.deactivate_fornecedor(db, fornecedor_id)


@router.get("/pedidos", response_model=List[PedidoCompraSummary])
def list_all_orders(
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin"))
) -> List[PedidoCompraSummary]:
    """Lista todos os pedidos do sistema para o perfil admin."""
    return pedido_service.listar_todos_pedidos(db)
