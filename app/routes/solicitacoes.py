from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import get_current_user
from app.models.user_db import User
from app.models.solicitacao_db import Solicitacao
from app.models.solicitacao import SolicitacaoCreate, SolicitacaoUpdate, SolicitacaoResponse

router = APIRouter()


@router.get("/", response_model=list[SolicitacaoResponse])
async def listar_solicitacoes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Solicitacao).where(Solicitacao.owner_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=SolicitacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_solicitacao(
    payload: SolicitacaoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    solicitacao = Solicitacao(
        titulo=payload.titulo,
        descricao=payload.descricao,
        categoria=payload.categoria,
        prioridade=payload.prioridade,
        owner_id=current_user.id,
    )
    db.add(solicitacao)
    await db.commit()
    await db.refresh(solicitacao)
    return solicitacao


@router.get("/{solicitacao_id}", response_model=SolicitacaoResponse)
async def buscar_solicitacao(
    solicitacao_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Solicitacao).where(
            Solicitacao.id == solicitacao_id,
            Solicitacao.owner_id == current_user.id,
        )
    )
    solicitacao = result.scalar_one_or_none()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    return solicitacao


@router.put("/{solicitacao_id}", response_model=SolicitacaoResponse)
async def atualizar_solicitacao(
    solicitacao_id: int,
    payload: SolicitacaoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Solicitacao).where(
            Solicitacao.id == solicitacao_id,
            Solicitacao.owner_id == current_user.id,
        )
    )
    solicitacao = result.scalar_one_or_none()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(solicitacao, key, value)

    await db.commit()
    await db.refresh(solicitacao)
    return solicitacao


@router.delete("/{solicitacao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_solicitacao(
    solicitacao_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Solicitacao).where(
            Solicitacao.id == solicitacao_id,
            Solicitacao.owner_id == current_user.id,
        )
    )
    solicitacao = result.scalar_one_or_none()
    if not solicitacao:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    await db.delete(solicitacao)
    await db.commit()
    return None