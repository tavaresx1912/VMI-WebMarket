from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.core.security import decode_access_token
from app.repositories import user_repository
from app.models.user import User

# auto_error=False permite que tratemos manualmente o erro de token ausente (retornando 401)
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependência que extrai e valida o usuário a partir do token JWT no header Authorization.

    Fluxo:
    1. Verifica se o token foi enviado — 401 se ausente.
    2. Decodifica e valida a assinatura do JWT — 401 se inválido/adulterado.
    3. Busca o usuário no banco pelo ID contido no token — 403 se não encontrado ou inativo.

    Verificamos 'ativo' no banco a cada requisição para que contas desativadas
    após a emissão do token percam acesso imediatamente.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido"
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id: int = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    user = user_repository.get_by_id(db, user_id)

    # Usuário não encontrado ou conta desativada após emissão do token
    if user is None or not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    return user


def require_role(*roles: str):
    """
    Fábrica de dependências que exige que o usuário autenticado possua um dos roles informados.
    Retorna 403 se o role do usuário não estiver na lista permitida.

    Exemplo de uso na rota:
        _ = Depends(require_role("admin"))
    """
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para esta operação"
            )
        return current_user
    return dependency
