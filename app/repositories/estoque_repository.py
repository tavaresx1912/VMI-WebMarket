from sqlalchemy.orm import Session
from app.models.estoque import Estoque


def get_by_id(db: Session, estoque_id: int) -> Estoque | None:
    """Retorna a entrada de estoque pelo ID, ou None se não existir."""
    return db.query(Estoque).filter(Estoque.id == estoque_id).first()


def get_by_produto_usuario(db: Session, produto_id: int, usuario_id: int) -> Estoque | None:
    """Retorna a entrada de estoque de um produto específico para um usuário."""
    return (
        db.query(Estoque)
        .filter(Estoque.produto_id == produto_id, Estoque.usuario_id == usuario_id)
        .first()
    )


def list_by_usuario(db: Session, usuario_id: int) -> list[Estoque]:
    """Lista todas as entradas de estoque de um usuário."""
    return db.query(Estoque).filter(Estoque.usuario_id == usuario_id).all()


def list_by_produtos(db: Session, produto_ids: list[int]) -> list[Estoque]:
    """Lista entradas de estoque para um conjunto de produtos (usado pelo fornecedor — VMI)."""
    if not produto_ids:
        return []
    return db.query(Estoque).filter(Estoque.produto_id.in_(produto_ids)).all()


def create(
    db: Session,
    produto_id: int,
    usuario_id: int,
    quantidade: int,
    ponto_reposicao: int,
    ponto_amarelo: int,
) -> Estoque:
    """Cria uma nova entrada de estoque."""
    estoque = Estoque(
        produto_id=produto_id,
        usuario_id=usuario_id,
        quantidade=quantidade,
        ponto_reposicao=ponto_reposicao,
        ponto_amarelo=ponto_amarelo,
    )
    db.add(estoque)
    db.commit()
    db.refresh(estoque)
    return estoque


def update_pontos(
    db: Session,
    estoque: Estoque,
    ponto_reposicao: int,
    ponto_amarelo: int,
) -> Estoque:
    """Atualiza os pontos de reposição configurados pelo usuário (RN-06)."""
    estoque.ponto_reposicao = ponto_reposicao
    estoque.ponto_amarelo = ponto_amarelo
    db.commit()
    db.refresh(estoque)
    return estoque


def update_quantidade(db: Session, estoque: Estoque, quantidade: int) -> Estoque:
    """Atualiza a quantidade disponível em estoque (usado pelo fornecedor — VMI, RN-03)."""
    estoque.quantidade = quantidade
    db.commit()
    db.refresh(estoque)
    return estoque
