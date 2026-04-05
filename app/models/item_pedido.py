from sqlalchemy import Column, Integer, ForeignKey, Float
from app.database import Base


class ItemPedido(Base):
    """
    Linha de um pedido de compra (RN-05).

    Referencia produto_fornecedor_id para rastrear qual fornecedor atende cada item,
    permitindo que um mesmo pedido tenha itens de fornecedores diferentes.
    O preco_unitario é registrado no momento do pedido (snapshot do contrato).
    """
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)

    # Pedido ao qual este item pertence
    pedido_id = Column(Integer, ForeignKey("pedidos_compra.id"), nullable=False)

    # Contrato específico (produto + fornecedor) que será acionado
    produto_fornecedor_id = Column(Integer, ForeignKey("produto_fornecedor.id"), nullable=False)

    quantidade = Column(Integer, nullable=False)

    # Snapshot do preço contratado no momento do pedido
    preco_unitario = Column(Float, nullable=False)
