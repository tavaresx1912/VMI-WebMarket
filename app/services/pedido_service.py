from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.fornecedor import Fornecedor
from app.models.produto_fornecedor import ProdutoFornecedor
from app.repositories import estoque_repository, pedido_compra_repository, item_pedido_repository
from app.schemas.item_pedido import ItemPedidoCreate, ItemPedidoResponse
from app.schemas.pedido_compra import PedidoCompraCreate, PedidoCompraSummary, PedidoCompraResponse
from app.services.estoque_service import calcular_status_kanban, _get_fornecedor_ou_404


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _get_contrato_ou_404(db: Session, produto_fornecedor_id: int) -> ProdutoFornecedor:
    """Retorna o contrato (ProdutoFornecedor) pelo ID, ou 404 se não existir."""
    contrato = db.query(ProdutoFornecedor).filter(ProdutoFornecedor.id == produto_fornecedor_id).first()
    if contrato is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contrato produto-fornecedor {produto_fornecedor_id} não encontrado"
        )
    return contrato


def _to_summary(pedido) -> PedidoCompraSummary:
    return PedidoCompraSummary(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        status=pedido.status,
        origem=pedido.origem,
        criado_em=pedido.criado_em,
    )


def _to_response(db: Session, pedido) -> PedidoCompraResponse:
    """Monta o detalhe completo do pedido com seus itens."""
    itens_orm = item_pedido_repository.list_by_pedido(db, pedido.id)
    itens = [
        ItemPedidoResponse(
            id=i.id,
            pedido_id=i.pedido_id,
            produto_fornecedor_id=i.produto_fornecedor_id,
            quantidade=i.quantidade,
            preco_unitario=i.preco_unitario,
        )
        for i in itens_orm
    ]
    return PedidoCompraResponse(
        id=pedido.id,
        usuario_id=pedido.usuario_id,
        status=pedido.status,
        origem=pedido.origem,
        criado_em=pedido.criado_em,
        itens=itens,
    )


# ---------------------------------------------------------------------------
# Operações do Usuário
# ---------------------------------------------------------------------------

def criar_pedido_manual(
    db: Session, usuario_id: int, data: PedidoCompraCreate
) -> PedidoCompraResponse:
    """
    Cria um pedido de compra manualmente (RN-05).
    Valida cada contrato referenciado e registra o preco_unitario do contrato como snapshot.
    """
    if not data.itens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O pedido deve conter ao menos um item"
        )

    pedido = pedido_compra_repository.create(db, usuario_id=usuario_id, origem="manual")

    for item_data in data.itens:
        contrato = _get_contrato_ou_404(db, item_data.produto_fornecedor_id)
        item_pedido_repository.create(
            db,
            pedido_id=pedido.id,
            produto_fornecedor_id=contrato.id,
            quantidade=item_data.quantidade,
            preco_unitario=contrato.preco_contratado,
        )

    return _to_response(db, pedido)


def criar_pedido_automatico(
    db: Session, usuario_id: int, estoque_id: int
) -> PedidoCompraResponse:
    """
    Cria automaticamente um pedido de reposição quando o estoque está em Amarelo ou
    Vermelho (RN-07).

    Fluxo:
    1. Valida que o estoque pertence ao usuário.
    2. Verifica que o status Kanban é Amarelo ou Vermelho.
    3. Usa o fornecedor marcado como preferencial no contrato.
    4. Cria o pedido com origem="automatico" e quantidade = qtd_minima_pedido do contrato.
    """
    estoque = estoque_repository.get_by_id(db, estoque_id)
    if estoque is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estoque não encontrado")
    if estoque.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    kanban = calcular_status_kanban(
        estoque.quantidade, estoque.ponto_reposicao, estoque.ponto_amarelo
    )
    if kanban == "verde":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Estoque saudável — pedido automático não é necessário"
        )

    # Busca o fornecedor preferencial para este produto (RN-07)
    contrato = (
        db.query(ProdutoFornecedor)
        .filter(
            ProdutoFornecedor.produto_id == estoque.produto_id,
            ProdutoFornecedor.preferencial == True,  # noqa: E712
        )
        .first()
    )
    if contrato is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nenhum fornecedor preferencial definido para este produto"
        )

    pedido = pedido_compra_repository.create(db, usuario_id=usuario_id, origem="automatico")
    item_pedido_repository.create(
        db,
        pedido_id=pedido.id,
        produto_fornecedor_id=contrato.id,
        quantidade=contrato.qtd_minima_pedido,
        preco_unitario=contrato.preco_contratado,
    )

    return _to_response(db, pedido)


def listar_pedidos_usuario(db: Session, usuario_id: int) -> list[PedidoCompraSummary]:
    """Lista todos os pedidos do usuário do mais recente ao mais antigo."""
    pedidos = pedido_compra_repository.list_by_usuario(db, usuario_id)
    return [_to_summary(p) for p in pedidos]


def detalhar_pedido(
    db: Session, usuario_id: int, pedido_id: int
) -> PedidoCompraResponse:
    """Retorna o detalhe de um pedido. Somente o dono do pedido tem acesso (RN-04)."""
    pedido = pedido_compra_repository.get_by_id(db, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    if pedido.usuario_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    return _to_response(db, pedido)


# ---------------------------------------------------------------------------
# Operações do Fornecedor
# ---------------------------------------------------------------------------

def listar_pedidos_fornecedor(
    db: Session, fornecedor_user_id: int
) -> list[PedidoCompraSummary]:
    """
    Lista os pedidos que contêm itens do fornecedor (RN-04).
    O fornecedor vê apenas os pedidos relacionados aos seus produtos.
    """
    fornecedor = _get_fornecedor_ou_404(db, fornecedor_user_id)
    pedido_ids = item_pedido_repository.list_pedido_ids_por_fornecedor(db, fornecedor.id)
    pedidos = pedido_compra_repository.list_by_pedido_ids(db, pedido_ids)
    return [_to_summary(p) for p in pedidos]


def atualizar_status_pedido(
    db: Session,
    fornecedor_user_id: int,
    pedido_id: int,
    novo_status: str,
) -> PedidoCompraSummary:
    """
    O fornecedor atualiza o status de um pedido (RN-05).
    Valida que o pedido contém ao menos um item do fornecedor.
    """
    fornecedor = _get_fornecedor_ou_404(db, fornecedor_user_id)
    pedido_ids = item_pedido_repository.list_pedido_ids_por_fornecedor(db, fornecedor.id)

    pedido = pedido_compra_repository.get_by_id(db, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado")
    if pedido.id not in pedido_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este pedido não contém itens do seu catálogo"
        )

    pedido = pedido_compra_repository.update_status(db, pedido, novo_status)
    return _to_summary(pedido)
