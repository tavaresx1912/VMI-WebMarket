import os
import bcrypt
from jose import jwt, JWTError

# Chave secreta usada para assinar os tokens JWT — em produção, usar variável de ambiente
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-troque-em-producao")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """
    Gera o hash bcrypt da senha.
    O salt é gerado aleatoriamente a cada chamada (comportamento padrão do bcrypt),
    por isso o mesmo input sempre gera hashes diferentes.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado usando comparação segura."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(payload: dict) -> str:
    """Cria um token JWT assinado com a SECRET_KEY. O payload deve conter 'sub' (como string) e 'role'."""
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida um token JWT.
    Lança JWTError se o token for inválido ou tiver sido adulterado.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
