from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.schemas.estoque import EstoqueCreate, EstoquePontosUpdate, EstoqueResponse
from app.schemas.pedido_compra import PedidoCompraCreate, PedidoCompraSummary, PedidoCompraResponse
from app.services import estoque_service, pedido_service

router = APIRouter(prefix="/usuario", tags=["Usuário"])


# ---------------------------------------------------------------------------
# Estoque
# ---------------------------------------------------------------------------

@router.post("/estoque", response_model=EstoqueResponse, status_code=201)
def criar_estoque(
    data: EstoqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("usuario")),
) -> EstoqueResponse:
    """
    Cria uma entrada de estoque para o produto informado.
    O usuário define os pontos de reposição iniciais (RN-06).
    """
    return estoque_service.criar_estoque(db, current_user.id, data)


@router.get("/estoque", response_model=List[EstoqueResponse])
def listar_estoque(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("usuario")),
) -> List[EstoqueResponse]:
    """
    Lista todo o estoque do usuário com semáforo Kanban calculado (RN-06).
    Itens em Amarelo ou Vermelho habilitam o pedido automático (RN-07).
    """
    return estoque_service.listar_estoque_usuario(db, current_user.id)


@router.patch("/estoque/{estoque_id}/pontos", response_model=EstoqueResponse)
def configurar_pontos(
    estoque_id: int,
    data: EstoquePontosUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("usuario")),
) -> EstoqueResponse:
    """Configura os pontos de reposição e amarelo de um item de estoque (RN-06)."""
    return estoque_service.configurar_pontos(db, current_user.id, estoque_id, data)


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------

@router.post("/pedidos", response_model=PedidoCompraResponse, status_code=201)
def criar_pedido_manual(
    data: PedidoCompraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("usuario")),
) -> PedidoCompraResponse:
    """Cria um pedido de compra manualmente com os itens e contratos informados (RN-05)."""
    return pedido_service.criar_pedido_manual(db, current_user.id, data)


@router.post("/pedidos/automatico/{estoque_id}", response_model=PedidoCompraResponse, status_code=201)
def criar_pedido_automatico(
    estoque_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("usuario")),
) -> PedidoCompraResponse:
    """
    Dispara um pedido de reposição automático para o estoque informado (RN-07).
    Só é permitido quando o semáforo está em Amarelo ou Vermelho.
    Usa o fornecedor preferencial e a quantidade mínima do contrato.
    """
    return pedido_service.criar_pedido_automatico(db, current_user.id, estoque_id)


@router.get("/pedidos", response_model=List[PedidoCompraSummary])
def listar_pedidos(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("usuario")),
) -> List[PedidoCompraSummary]:
    """Lista todos os pedidos do usuário, do mais recente ao mais antigo (RN-04)."""
    return pedido_service.listar_pedidos_usuario(db, current_user.id)


@router.get("/pedidos/{pedido_id}", response_model=PedidoCompraResponse)
def detalhar_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("usuario")),
) -> PedidoCompraResponse:
    """Retorna o detalhe completo de um pedido com seus itens (RN-04)."""
    return pedido_service.detalhar_pedido(db, current_user.id, pedido_id)
