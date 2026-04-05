from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.estoque import Estoque
from app.models.fornecedor import Fornecedor
from app.models.produto_fornecedor import ProdutoFornecedor
from app.repositories import estoque_repository
from app.schemas.estoque import EstoqueCreate, EstoquePontosUpdate, EstoqueQuantidadeUpdate, EstoqueResponse


# ---------------------------------------------------------------------------
# Funções puras — sem acesso ao banco
# ---------------------------------------------------------------------------

def calcular_status_kanban(quantidade: int, ponto_reposicao: int, ponto_amarelo: int) -> str:
    """
    Calcula o semáforo Kanban de um item de estoque (RN-06).

    Regras:
        verde    — quantidade >= ponto_amarelo
        amarelo  — ponto_reposicao < quantidade < ponto_amarelo
        vermelho — quantidade <= ponto_reposicao
    """
    if quantidade >= ponto_amarelo:
        return "verde"
    if quantidade <= ponto_reposicao:
        return "vermelho"
    return "amarelo"


def _to_response(estoque: Estoque) -> EstoqueResponse:
    """Converte o ORM Estoque para EstoqueResponse com status_kanban calculado."""
    return EstoqueResponse(
        id=estoque.id,
        produto_id=estoque.produto_id,
        usuario_id=estoque.usuario_id,
        quantidade=estoque.quantidade,
        ponto_reposicao=estoque.ponto_reposicao,
        ponto_amarelo=estoque.ponto_amarelo,
        status_kanban=calcular_status_kanban(
            estoque.quantidade, estoque.ponto_reposicao, estoque.ponto_amarelo
        ),
    )


# ---------------------------------------------------------------------------
# Operações do Usuário
# ---------------------------------------------------------------------------

def criar_estoque(db: Session, usuario_id: int, data: EstoqueCreate) -> EstoqueResponse:
    """
    Cria uma entrada de estoque para o usuário.
    Retorna 409 se já existir estoque para esse produto e usuário.
    """
    existente = estoque_repository.get_by_produto_usuario(db, data.produto_id, usuario_id)
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Estoque já cadastrado para este produto"
        )
    estoque = estoque_repository.create(
        db,
        produto_id=data.produto_id,
        usuario_id=usuario_id,
        quantidade=data.quantidade,
        ponto_reposicao=data.ponto_reposicao,
        ponto_amarelo=data.ponto_amarelo,
    )
    return _to_response(estoque)


def listar_estoque_usuario(db: Session, usuario_id: int) -> list[EstoqueResponse]:
    """Lista todo o estoque do usuário com semáforo Kanban calculado (RN-06)."""
    itens = estoque_repository.list_by_usuario(db, usuario_id)
    return [_to_response(e) for e in itens]


def configurar_pontos(
    db: Session,
    usuario_id: int,
    estoque_id: int,
    data: EstoquePontosUpdate,
) -> EstoqueResponse:
    """
    Atualiza ponto_reposicao e ponto_amarelo de uma entrada de estoque.
    Apenas o dono do estoque pode configurar os pontos (RN-04).
    """
    estoque = estoque_repository.get_by_id(db, estoque_id)
    if estoque is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estoque não encontrado")
    if estoque.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    estoque = estoque_repository.update_pontos(db, estoque, data.ponto_reposicao, data.ponto_amarelo)
    return _to_response(estoque)


# ---------------------------------------------------------------------------
# Operações do Fornecedor (VMI — RN-03)
# ---------------------------------------------------------------------------

def _get_fornecedor_ou_404(db: Session, user_id: int) -> Fornecedor:
    """Retorna o Fornecedor vinculado ao user_id, ou 404 se não cadastrado."""
    fornecedor = db.query(Fornecedor).filter(Fornecedor.user_id == user_id).first()
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado para este usuário"
        )
    return fornecedor


def _produto_ids_do_fornecedor(db: Session, fornecedor_id: int) -> list[int]:
    """Retorna os IDs dos produtos vinculados ao fornecedor."""
    rows = (
        db.query(ProdutoFornecedor.produto_id)
        .filter(ProdutoFornecedor.fornecedor_id == fornecedor_id)
        .all()
    )
    return [r[0] for r in rows]


def listar_estoque_fornecedor(db: Session, fornecedor_user_id: int) -> list[EstoqueResponse]:
    """
    Lista o estoque de todos os produtos vinculados ao fornecedor,
    para todos os usuários clientes (visão VMI — RN-03, RN-04).
    """
    fornecedor = _get_fornecedor_ou_404(db, fornecedor_user_id)
    produto_ids = _produto_ids_do_fornecedor(db, fornecedor.id)
    itens = estoque_repository.list_by_produtos(db, produto_ids)
    return [_to_response(e) for e in itens]


def atualizar_quantidade(
    db: Session,
    fornecedor_user_id: int,
    estoque_id: int,
    data: EstoqueQuantidadeUpdate,
) -> EstoqueResponse:
    """
    O fornecedor atualiza a quantidade disponível em estoque (VMI — RN-03).
    Retorna 403 se o produto do estoque não pertencer ao fornecedor.
    """
    fornecedor = _get_fornecedor_ou_404(db, fornecedor_user_id)
    produto_ids = _produto_ids_do_fornecedor(db, fornecedor.id)

    estoque = estoque_repository.get_by_id(db, estoque_id)
    if estoque is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estoque não encontrado")
    if estoque.produto_id not in produto_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este produto não pertence ao seu catálogo"
        )

    estoque = estoque_repository.update_quantidade(db, estoque, data.quantidade)
    return _to_response(estoque)
