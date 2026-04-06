from sqlalchemy.orm import Session
from app.models.fornecedor import Fornecedor


def get_by_id(db: Session, fornecedor_id: int) -> Fornecedor | None:
    """Busca um fornecedor pelo ID."""
    return db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()


def get_by_user_id(db: Session, user_id: int) -> Fornecedor | None:
    """Busca um fornecedor pelo user_id vinculado."""
    return db.query(Fornecedor).filter(Fornecedor.user_id == user_id).first()


def get_by_cnpj(db: Session, cnpj: str) -> Fornecedor | None:
    """Busca um fornecedor pelo CNPJ."""
    return db.query(Fornecedor).filter(Fornecedor.cnpj == cnpj).first()


def get_all(db: Session) -> list[Fornecedor]:
    """Retorna todos os fornecedores cadastrados."""
    return db.query(Fornecedor).all()


def create(db: Session, fornecedor: Fornecedor) -> Fornecedor:
    """Persiste um novo fornecedor no banco e retorna o objeto atualizado."""
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor
