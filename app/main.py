from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine

import app.models.user  # noqa: F401
import app.models.fornecedor  # noqa: F401
import app.models.produto  # noqa: F401
import app.models.produto_fornecedor  # noqa: F401
import app.models.estoque  # noqa: F401
import app.models.pedido_compra  # noqa: F401
import app.models.item_pedido  # noqa: F401

from app.routes import admin, auth, fornecedor_estoque, usuario


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria as tabelas no banco de dados ao iniciar a aplicação (se não existirem)."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="VMI WebMarket",
    version="0.2",
    description="Plataforma de e-commerce baseada no modelo VMI (Vendor Managed Inventory)",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(usuario.router)
app.include_router(fornecedor_estoque.router)
