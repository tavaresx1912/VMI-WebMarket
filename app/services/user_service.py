from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.algorithms.search import contains_text, filter_by_predicate
from app.repositories import user_repository
from app.models.user import User
from app.core.security import hash_password


def create_user(db: Session, nome: str, email: str, senha: str, role: str) -> User:
    """
    Cria um novo usuário no sistema.
    Apenas o admin pode chamar este serviço (controle feito na rota).

    Lança 400 se o email já estiver cadastrado (email é único no sistema).
    """
    existing = user_repository.get_by_email(db, email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )

    user = User(
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        role=role,
        ativo=True
    )
    return user_repository.create(db, user)


def list_users(db: Session, search_term: str | None = None) -> list[User]:
    """
    Retorna todos os usuários cadastrados.
    Quando search_term é informado, aplica busca linear manual por nome ou email.
    """
    users = user_repository.get_all(db)
    if search_term is None or search_term.strip() == "":
        return users

    return filter_by_predicate(
        users,
        lambda user: contains_text(user.nome, search_term) or contains_text(user.email, search_term)
    )


def deactivate_user(db: Session, user_id: int) -> User:
    """
    Desativa a conta de um usuário pelo ID.
    Conta desativada impede login (verificado no auth_service).

    Lança 404 se o usuário não for encontrado.
    """
    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    user.ativo = False
    db.commit()
    db.refresh(user)
    return user
