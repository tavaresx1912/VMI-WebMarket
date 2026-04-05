from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.database import Base


class PedidoCompra(Base):
    """
    Cabeçalho de um pedido de compra criado pelo usuário (RN-05).

    status: ciclo de vida do pedido
        pendente → confirmado → enviado → entregue | cancelado

    origem: rastreabilidade do pedido (RN-07)
        "manual"    — criado explicitamente pelo usuário
        "automatico" — disparado pelo sistema via semáforo Kanban
    """
    __tablename__ = "pedidos_compra"

    id = Column(Integer, primary_key=True, index=True)

    # Usuário que gerou o pedido
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Status atual do pedido
    status = Column(String, default="pendente", nullable=False)

    # Origem para rastreabilidade: "manual" ou "automatico"
    origem = Column(String, nullable=False)

    # Data/hora de criação — gerada em Python para compatibilidade com SQLite
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
