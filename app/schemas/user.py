from pydantic import BaseModel, EmailStr
from typing import Literal


class UserCreate(BaseModel):
    """Schema de entrada para criação de usuário pelo admin."""
    nome: str
    email: EmailStr
    senha: str
    role: Literal["admin", "usuario", "fornecedor"]


class UserResponse(BaseModel):
    """
    Schema de saída para dados de usuário.
    Nunca expõe senha ou senha_hash — apenas campos seguros.
    """
    id: int
    nome: str
    email: str
    role: str
    ativo: bool

    # from_attributes=True permite que o Pydantic leia atributos de objetos SQLAlchemy
    model_config = {"from_attributes": True}
