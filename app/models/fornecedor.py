from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class Fornecedor(Base):
    """
    Stub do modelo Fornecedor — tabela gerenciada pela Pessoa 2 (domínio produto/contrato).
    Definida aqui apenas para satisfazer as chaves estrangeiras de ProdutoFornecedor.
    """
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)

    # Referência ao usuário com role="fornecedor"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    nome = Column(String, nullable=False)
    cnpj = Column(String, unique=True, nullable=False)
