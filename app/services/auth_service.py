from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import user_repository
from app.core.security import verify_password, create_access_token


def login(db: Session, email: str, password: str) -> dict:
    """
    Autentica o usuário verificando email e senha.

    Fluxo:
    1. Busca o usuário pelo email — retorna 401 se não encontrado.
    2. Verifica a senha com bcrypt — retorna 401 se incorreta.
    3. Verifica se a conta está ativa — retorna 403 se desativada.
    4. Gera e retorna o token JWT com 'sub' (id como string) e 'role'.

    Retornamos 401 para credenciais erradas (não revelamos se o email existe).
    """
    user = user_repository.get_by_email(db, email)

    # Verificamos email e senha juntos para não revelar qual dos dois está errado
    if user is None or not verify_password(password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    # Conta desativada pelo admin — código 403 (identificado, mas sem permissão)
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Entre em contato com o administrador."
        )

    # sub deve ser string conforme RFC 7519
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
