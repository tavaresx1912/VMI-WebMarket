import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.core.security import hash_password

# Banco em memória para testes — StaticPool garante que todas as sessões compartilham
# a mesma conexão (necessário para SQLite in-memory funcionar entre sessões distintas)
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    """Cria as tabelas antes de cada teste e remove depois — garante isolamento total."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Fornece uma sessão de banco de dados para uso direto nos testes."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """
    Fornece um TestClient do FastAPI com o banco de dados de teste injetado.
    O override de get_db faz com que a aplicação use a mesma sessão do fixture 'db',
    permitindo que dados inseridos no teste sejam vistos pela aplicação.
    """
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    """Cria e persiste um usuário admin para uso nos testes que exigem autenticação."""
    user = User(
        nome="Admin",
        email="admin@test.com",
        senha_hash=hash_password("admin123"),
        role="admin",
        ativo=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, admin_user):
    """Retorna os headers de autorização com token JWT válido do admin."""
    resp = client.post("/auth/login", json={"email": "admin@test.com", "senha": "admin123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
