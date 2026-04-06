import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.fornecedor import Fornecedor
from app.models.produto import Produto
from app.models.produto_fornecedor import ProdutoFornecedor
from app.models.estoque import Estoque
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


# ---------------------------------------------------------------------------
# Fixtures do domínio de inventário
# ---------------------------------------------------------------------------

@pytest.fixture
def usuario_user(db):
    """Cria um usuário com role='usuario'."""
    user = User(
        nome="Usuario Teste",
        email="usuario@test.com",
        senha_hash=hash_password("usuario123"),
        role="usuario",
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def usuario_headers(client, usuario_user):
    """Headers JWT do usuário comum."""
    resp = client.post("/auth/login", json={"email": "usuario@test.com", "senha": "usuario123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fornecedor_user(db):
    """Cria um usuário com role='fornecedor'."""
    user = User(
        nome="Fornecedor Teste",
        email="fornecedor@test.com",
        senha_hash=hash_password("forn123"),
        role="fornecedor",
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def fornecedor_headers(client, fornecedor_user, fornecedor_entity):
    """Headers JWT do fornecedor."""
    resp = client.post("/auth/login", json={"email": "fornecedor@test.com", "senha": "forn123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def fornecedor_entity(db, fornecedor_user):
    """Cria o registro Fornecedor vinculado ao usuário fornecedor."""
    fornecedor = Fornecedor(
        user_id=fornecedor_user.id,
        nome="Fornecedor Ltda",
        cnpj="12.345.678/0001-99",
    )
    db.add(fornecedor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor


@pytest.fixture
def produto(db):
    """Cria um Produto de teste."""
    p = Produto(nome="Caneta Azul", descricao="Caneta esferográfica azul", categoria="Papelaria")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@pytest.fixture
def contrato(db, produto, fornecedor_entity):
    """
    Cria um contrato ProdutoFornecedor preferencial entre o produto e o fornecedor.
    Usado para testes de pedido automático (RN-07).
    """
    pf = ProdutoFornecedor(
        produto_id=produto.id,
        fornecedor_id=fornecedor_entity.id,
        preferencial=True,
        preco_contratado=4.50,
        prazo_entrega_dias=3,
        qtd_minima_pedido=10,
    )
    db.add(pf)
    db.commit()
    db.refresh(pf)
    return pf


@pytest.fixture
def estoque(db, produto, usuario_user):
    """Cria uma entrada de estoque com semáforo em verde (quantidade acima de ponto_amarelo)."""
    e = Estoque(
        produto_id=produto.id,
        usuario_id=usuario_user.id,
        quantidade=50,
        ponto_reposicao=10,
        ponto_amarelo=20,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e
