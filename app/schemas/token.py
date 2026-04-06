from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema de entrada para o endpoint de login."""
    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    """Schema de saída do endpoint de login — retorna o JWT e o tipo do token."""
    access_token: str
    token_type: str
