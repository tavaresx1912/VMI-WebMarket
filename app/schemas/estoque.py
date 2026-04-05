from pydantic import BaseModel
from typing import Literal


class EstoqueCreate(BaseModel):
    """Dados para criar uma entrada de estoque para um produto."""
    produto_id: int
    quantidade: int = 0
    ponto_reposicao: int = 0
    ponto_amarelo: int = 0


class EstoquePontosUpdate(BaseModel):
    """Atualiza os limiares de alerta do semáforo Kanban (configurado pelo usuário — RN-06)."""
    ponto_reposicao: int
    ponto_amarelo: int


class EstoqueQuantidadeUpdate(BaseModel):
    """Atualiza a quantidade disponível em estoque (usado pelo fornecedor — VMI, RN-03)."""
    quantidade: int


class EstoqueResponse(BaseModel):
    """
    Resposta de estoque com semáforo Kanban calculado (RN-06).

    status_kanban:
        verde    — quantidade >= ponto_amarelo (estoque saudável)
        amarelo  — ponto_reposicao < quantidade < ponto_amarelo (atenção)
        vermelho — quantidade <= ponto_reposicao (crítico)
    """
    id: int
    produto_id: int
    usuario_id: int
    quantidade: int
    ponto_reposicao: int
    ponto_amarelo: int
    status_kanban: Literal["verde", "amarelo", "vermelho"]

    model_config = {"from_attributes": True}
