"""
Rotas do Fornecedor para estoque e pedidos (Pessoa 3).

Este arquivo foi separado para evitar misturar o domínio de inventário/pedidos
com futuros endpoints de catálogo e contratos do fornecedor.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.schemas.estoque import EstoqueQuantidadeUpdate, EstoqueResponse
from app.schemas.pedido_compra import PedidoCompraSummary, PedidoCompraStatusUpdate
from app.services import estoque_service, pedido_service

router = APIRouter(prefix="/fornecedor", tags=["Fornecedor"])


@router.get("/estoque", response_model=List[EstoqueResponse])
def listar_estoque(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("fornecedor")),
) -> List[EstoqueResponse]:
    """
    Lista o estoque de todos os produtos do fornecedor para todos os clientes vinculados.
    Permite ao fornecedor monitorar os níveis de reposição (VMI - RN-03, RN-04).
    """
    return estoque_service.listar_estoque_fornecedor(db, current_user.id)


@router.patch("/estoque/{estoque_id}", response_model=EstoqueResponse)
def atualizar_quantidade(
    estoque_id: int,
    data: EstoqueQuantidadeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("fornecedor")),
) -> EstoqueResponse:
    """
    Atualiza a quantidade disponível em estoque para um cliente (VMI - RN-03).
    O semáforo Kanban é recalculado automaticamente após a atualização.
    """
    return estoque_service.atualizar_quantidade(db, current_user.id, estoque_id, data)


@router.get("/pedidos", response_model=List[PedidoCompraSummary])
def listar_pedidos(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("fornecedor")),
) -> List[PedidoCompraSummary]:
    """
    Lista todos os pedidos que contêm itens do fornecedor (RN-04).
    Inclui pedidos manuais e automáticos.
    """
    return pedido_service.listar_pedidos_fornecedor(db, current_user.id)


@router.patch("/pedidos/{pedido_id}/status", response_model=PedidoCompraSummary)
def atualizar_status_pedido(
    pedido_id: int,
    data: PedidoCompraStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("fornecedor")),
) -> PedidoCompraSummary:
    """
    Atualiza o status de um pedido (RN-05).
    O fornecedor só pode atualizar pedidos que contêm seus produtos.
    """
    return pedido_service.atualizar_status_pedido(db, current_user.id, pedido_id, data.status)
