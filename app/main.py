from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, admin


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

# Registra os roteadores com seus prefixos
app.include_router(auth.router)
app.include_router(admin.router)
