from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.database import Base


class Estoque(Base):
    """
    Representa o estoque de um produto para um usuário específico (modelo VMI — RN-03).

    O usuário configura os pontos de reposição; o fornecedor atualiza a quantidade.
    O semáforo Kanban (verde/amarelo/vermelho) é calculado a partir de
    quantidade vs. ponto_amarelo vs. ponto_reposicao (RN-06).

    Restrição: cada usuário só pode ter uma entrada de estoque por produto.
    """
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True)

    # Produto monitorado
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)

    # Usuário dono do estoque
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Quantidade atual em estoque — atualizada pelo fornecedor (VMI)
    quantidade = Column(Integer, default=0, nullable=False)

    # Limiar de alerta vermelho: quantidade <= ponto_reposicao → status crítico
    ponto_reposicao = Column(Integer, default=0, nullable=False)

    # Limiar de alerta amarelo: ponto_reposicao < quantidade < ponto_amarelo → atenção
    ponto_amarelo = Column(Integer, default=0, nullable=False)

    # Garante que um usuário não tenha duas entradas para o mesmo produto
    __table_args__ = (
        UniqueConstraint("produto_id", "usuario_id", name="uq_estoque_produto_usuario"),
    )
