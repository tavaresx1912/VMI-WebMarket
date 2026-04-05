from sqlalchemy.orm import Session
from app.models.item_pedido import ItemPedido


def list_by_pedido(db: Session, pedido_id: int) -> list[ItemPedido]:
    """Lista todos os itens de um pedido."""
    return db.query(ItemPedido).filter(ItemPedido.pedido_id == pedido_id).all()


def list_pedido_ids_por_fornecedor(db: Session, fornecedor_id: int) -> list[int]:
    """
    Retorna os IDs de pedidos que contêm itens fornecidos pelo fornecedor informado.
    Usado para que o fornecedor veja apenas os pedidos que lhe dizem respeito (RN-04).
    """
    from app.models.produto_fornecedor import ProdutoFornecedor

    # Busca os IDs únicos de pedidos que possuem itens vinculados a este fornecedor
    rows = (
        db.query(ItemPedido.pedido_id)
        .join(ProdutoFornecedor, ProdutoFornecedor.id == ItemPedido.produto_fornecedor_id)
        .filter(ProdutoFornecedor.fornecedor_id == fornecedor_id)
        .distinct()
        .all()
    )
    return [row[0] for row in rows]


def create(
    db: Session,
    pedido_id: int,
    produto_fornecedor_id: int,
    quantidade: int,
    preco_unitario: float,
) -> ItemPedido:
    """Cria um item de pedido com snapshot do preço contratado."""
    item = ItemPedido(
        pedido_id=pedido_id,
        produto_fornecedor_id=produto_fornecedor_id,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
