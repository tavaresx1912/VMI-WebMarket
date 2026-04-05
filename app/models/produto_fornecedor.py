from sqlalchemy import Column, Integer, ForeignKey, Boolean, Float
from app.database import Base


class ProdutoFornecedor(Base):
    """
    Stub do modelo ProdutoFornecedor (contrato N:N) — tabela gerenciada pela Pessoa 2.
    Definida aqui para satisfazer a FK de ItemPedido e para o cálculo de pedido automático (RN-07).

    Campos relevantes para o domínio de inventário:
    - preferencial: indica o fornecedor padrão para reposição automática (RN-07)
    - preco_contratado: usado como preco_unitario no ItemPedido automático
    - qtd_minima_pedido: quantidade usada no pedido automático (RN-07)
    """
    __tablename__ = "produto_fornecedor"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=False)

    # True quando este fornecedor é o preferencial para reposição automática
    preferencial = Column(Boolean, default=False, nullable=False)

    preco_contratado = Column(Float, nullable=False)
    prazo_entrega_dias = Column(Integer, nullable=False)
    qtd_minima_pedido = Column(Integer, nullable=False)
