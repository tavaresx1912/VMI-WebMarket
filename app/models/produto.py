from sqlalchemy import Column, Integer, String
from app.database import Base


class Produto(Base):
    """
    Stub do modelo Produto — tabela gerenciada pela Pessoa 2 (domínio produto/contrato).
    Definida aqui apenas para satisfazer as chaves estrangeiras de Estoque e ProdutoFornecedor.
    """
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
