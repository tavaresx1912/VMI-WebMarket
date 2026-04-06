from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.algorithms.search import contains_text, filter_by_predicate
from app.core.security import hash_password
from app.models.fornecedor import Fornecedor
from app.models.user import User
from app.repositories import fornecedor_repository, user_repository
from app.schemas.fornecedor import FornecedorResponse


def _to_response(fornecedor: Fornecedor, user: User) -> FornecedorResponse:
    """Monta a resposta do fornecedor junto com o status da conta vinculada."""
    return FornecedorResponse(
        id=fornecedor.id,
        user_id=fornecedor.user_id,
        nome=fornecedor.nome,
        email=user.email,
        cnpj=fornecedor.cnpj,
        ativo=user.ativo,
    )


def create_fornecedor(db: Session, nome: str, email: str, senha: str, cnpj: str) -> FornecedorResponse:
    """Cria um fornecedor e sua conta de acesso com role='fornecedor'."""
    existing_user = user_repository.get_by_email(db, email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    existing_fornecedor = fornecedor_repository.get_by_cnpj(db, cnpj)
    if existing_fornecedor is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )

    user = User(
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        role="fornecedor",
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    fornecedor = Fornecedor(user_id=user.id, nome=nome, cnpj=cnpj)
    fornecedor = fornecedor_repository.create(db, fornecedor)
    return _to_response(fornecedor, user)


def list_fornecedores(db: Session, search_term: str | None = None) -> list[FornecedorResponse]:
    """Lista fornecedores, com busca linear opcional por nome, email ou CNPJ."""
    fornecedores = fornecedor_repository.get_all(db)

    if search_term is not None and search_term.strip() != "":
        def matches_search(fornecedor: Fornecedor) -> bool:
            user = user_repository.get_by_id(db, fornecedor.user_id)
            if user is None:
                return False
            return (
                contains_text(fornecedor.nome, search_term)
                or contains_text(fornecedor.cnpj, search_term)
                or contains_text(user.email, search_term)
            )

        fornecedores = filter_by_predicate(fornecedores, matches_search)

    response_items: list[FornecedorResponse] = []
    for fornecedor in fornecedores:
        user = user_repository.get_by_id(db, fornecedor.user_id)
        if user is not None:
            response_items.append(_to_response(fornecedor, user))
    return response_items


def deactivate_fornecedor(db: Session, fornecedor_id: int) -> FornecedorResponse:
    """
    Desativa a conta vinculada a um fornecedor.
    O cadastro do fornecedor permanece para manter rastreabilidade.
    """
    fornecedor = fornecedor_repository.get_by_id(db, fornecedor_id)
    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )

    user = user_repository.get_by_id(db, fornecedor.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário vinculado ao fornecedor não encontrado"
        )

    user.ativo = False
    db.commit()
    db.refresh(user)
    return _to_response(fornecedor, user)
