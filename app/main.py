from fastapi import FastAPI

from app.routes import solicitacoes, auth
from app.database import init_db

app = FastAPI(title="Portal de Solicitações")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(solicitacoes.router, prefix="/solicitacoes", tags=["Solicitaçôes"])

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
def read_root():
    return {"mensagem": "API do Portal de Solixitações funcionando 🚀"}
