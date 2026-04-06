from pydantic import BaseModel, EmailStr


class FornecedorCreate(BaseModel):
    """Schema de entrada para cadastro de fornecedor pelo admin."""
    nome: str
    email: EmailStr
    senha: str
    cnpj: str


class FornecedorResponse(BaseModel):
    """Schema de saída de fornecedor com dados da conta vinculada."""
    id: int
    user_id: int
    nome: str
    email: str
    cnpj: str
    ativo: bool
