from pydantic import BaseModel


class ItemPedidoCreate(BaseModel):
    """Item para inclusão em um pedido manual (RN-05)."""
    produto_fornecedor_id: int
    quantidade: int


class ItemPedidoResponse(BaseModel):
    """Resposta de um item de pedido com snapshot de preço."""
    id: int
    pedido_id: int
    produto_fornecedor_id: int
    quantidade: int
    preco_unitario: float

    model_config = {"from_attributes": True}
