from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Generator

# URL do banco de dados — SQLite para desenvolvimento
SQLALCHEMY_DATABASE_URL = "sqlite:///./webmarket.db"

# check_same_thread=False necessário para SQLite com múltiplas threads (padrão do FastAPI)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Fábrica de sessões — autocommit e autoflush desativados para controle manual
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos SQLAlchemy do projeto."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependência do FastAPI que fornece uma sessão de banco de dados por requisição.
    A sessão é fechada automaticamente ao final da requisição (padrão try/finally).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
