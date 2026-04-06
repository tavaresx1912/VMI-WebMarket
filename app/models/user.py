from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class User(Base):
    """
    Modelo da tabela 'users'.
    Representa os três perfis do sistema: admin, usuario e fornecedor.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    # Perfil de acesso: "admin" | "usuario" | "fornecedor"
    role = Column(String, nullable=False)

    # Conta ativa ou desativada pelo admin
    ativo = Column(Boolean, default=True, nullable=False)
