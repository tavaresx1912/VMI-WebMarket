from sqlalchemy.orm import Session
from app.models.user import User


def get_by_email(db: Session, email: str) -> User | None:
    """
    Busca um usuário pelo email.
    Usa a query do SQLAlchemy com filtro direto — a busca manual por algoritmo
    é aplicada nas camadas de serviço quando operar sobre listas em memória.
    """
    return db.query(User).filter(User.email == email).first()


def get_by_id(db: Session, user_id: int) -> User | None:
    """Busca um usuário pelo ID primário."""
    return db.query(User).filter(User.id == user_id).first()


def get_all(db: Session) -> list[User]:
    """Retorna todos os usuários cadastrados."""
    return db.query(User).all()


def create(db: Session, user: User) -> User:
    """Persiste um novo usuário no banco e retorna o objeto atualizado com o ID gerado."""
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
