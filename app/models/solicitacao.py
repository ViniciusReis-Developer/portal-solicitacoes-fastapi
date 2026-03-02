from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class AdminUpdateSolicitacao(BaseModel):
    status: Optional[str] = None
    responsavel: Optional[str] = None


class SolicitacaoCreate(BaseModel):
    titulo: str
    descricao: str
    categoria: str
    prioridade: str


class SolicitacaoUpdate(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    categoria: str | None = None
    prioridade: str | None = None
    status: str | None = None
    responsavel: str | None = None


class SolicitacaoResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    categoria: str
    prioridade: str
    status: str
    criado_em: datetime
    atualizado_em: datetime
    responsavel: str | None
    owner_id: int

    class Config:
        from_attributes = True