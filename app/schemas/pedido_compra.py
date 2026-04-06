from datetime import datetime
from pydantic import BaseModel
from typing import List, Literal
from app.schemas.item_pedido import ItemPedidoCreate, ItemPedidoResponse


class PedidoCompraCreate(BaseModel):
    """Dados para criação de pedido manual (RN-05). Requer ao menos um item."""
    itens: List[ItemPedidoCreate]


class PedidoCompraStatusUpdate(BaseModel):
    """Atualização de status pelo fornecedor (RN-05)."""
    status: Literal["pendente", "confirmado", "enviado", "entregue", "cancelado"]


class PedidoCompraSummary(BaseModel):
    """Resumo do pedido para listagens — sem itens."""
    id: int
    usuario_id: int
    status: str
    origem: str
    criado_em: datetime

    model_config = {"from_attributes": True}


class PedidoCompraResponse(BaseModel):
    """Detalhe completo do pedido com seus itens."""
    id: int
    usuario_id: int
    status: str
    origem: str
    criado_em: datetime
    itens: List[ItemPedidoResponse]

    model_config = {"from_attributes": True}
