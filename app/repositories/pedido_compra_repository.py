from sqlalchemy.orm import Session
from app.models.pedido_compra import PedidoCompra


def get_by_id(db: Session, pedido_id: int) -> PedidoCompra | None:
    """Retorna um pedido pelo ID, ou None se não existir."""
    return db.query(PedidoCompra).filter(PedidoCompra.id == pedido_id).first()


def list_by_usuario(db: Session, usuario_id: int) -> list[PedidoCompra]:
    """Lista todos os pedidos de um usuário, ordenados do mais recente ao mais antigo."""
    return (
        db.query(PedidoCompra)
        .filter(PedidoCompra.usuario_id == usuario_id)
        .order_by(PedidoCompra.criado_em.desc())
        .all()
    )


def list_by_pedido_ids(db: Session, pedido_ids: list[int]) -> list[PedidoCompra]:
    """Lista pedidos a partir de um conjunto de IDs (usado pelo fornecedor)."""
    if not pedido_ids:
        return []
    return (
        db.query(PedidoCompra)
        .filter(PedidoCompra.id.in_(pedido_ids))
        .order_by(PedidoCompra.criado_em.desc())
        .all()
    )


def create(db: Session, usuario_id: int, origem: str) -> PedidoCompra:
    """Cria o cabeçalho de um novo pedido de compra com status 'pendente'."""
    pedido = PedidoCompra(
        usuario_id=usuario_id,
        status="pendente",
        origem=origem,
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


def update_status(db: Session, pedido: PedidoCompra, novo_status: str) -> PedidoCompra:
    """Atualiza o status de um pedido."""
    pedido.status = novo_status
    db.commit()
    db.refresh(pedido)
    return pedido
