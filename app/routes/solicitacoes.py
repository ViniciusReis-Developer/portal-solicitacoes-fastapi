from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.auth import get_current_admin
from app.auth import get_current_user
from app.models.user_db import User
from app.models.solicitacao_db import Solicitacao
from app.models.solicitacao import SolicitacaoCreate, SolicitacaoUpdate, SolicitacaoResponse, AdminUpdateSolicitacao

router = APIRouter()


@router.get("/admin/todas")
async def listar_todas_solicitacoes(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Solicitacao))
    return result.scalars().all()


@router.get("/")
async def listar_solicitacoes(
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    categoria: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = select(Solicitacao)

    # USER vê apenas as próprias
    if current_user.role != "admin":
        query = query.where(Solicitacao.owner_id == current_user.id)

    if status:
        query = query.where(Solicitacao.status == status)

    if prioridade:
        query = query.where(Solicitacao.prioridade == prioridade)

    if categoria:
        query = query.where(Solicitacao.categoria == categoria)

    result = await db.execute(query)

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


@router.post("/admin/{solicitacao_id}/assumir")
async def admin_assumir(
    solicitacao_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Solicitacao).where(Solicitacao.id == solicitacao_id))
    sol = result.scalar_one_or_none()

    if not sol:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    sol.responsavel = admin.username
    if sol.status == "aberta":
        sol.status = "em_andamento"

    await db.commit()
    await db.refresh(sol)
    return sol


@router.get("/stats")
async def stats_solicitacoes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    base_filter = []
    if current_user.role != "admin":
        base_filter.append(Solicitacao.owner_id == current_user.id)

    # total
    result_total = await db.execute(select(func.count()).select_from(Solicitacao).where(*base_filter))
    total = result_total.scalar_one()

    # por status
    result_status = await db.execute(
        select(Solicitacao.status, func.count())
        .where(*base_filter)
        .group_by(Solicitacao.status)
    )
    por_status = {status: count for status, count in result_status.all()}

    # por prioridade
    result_prioridade = await db.execute(
        select(Solicitacao.prioridade, func.count())
        .where(*base_filter)
        .group_by(Solicitacao.prioridade)
    )
    por_prioridade = {prio: count for prio, count in result_prioridade.all()}

    # por categoria
    result_categoria = await db.execute(
        select(Solicitacao.categoria, func.count())
        .where(*base_filter)
        .group_by(Solicitacao.categoria)
    )
    por_categoria = {cat: count for cat, count in result_categoria.all()}

    return {
        "total": total,
        "por_status": por_status,
        "por_prioridade": por_prioridade,
        "por_categoria": por_categoria,
    }


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


@router.put("/admin/{solicitacao_id}")
async def admin_update_solicitacao(
    solicitacao_id: int,
    payload: AdminUpdateSolicitacao,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Solicitacao).where(Solicitacao.id == solicitacao_id))
    sol = result.scalar_one_or_none()

    if not sol:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if payload.status is not None:
        sol.status = payload.status

    if payload.responsavel is not None:
        sol.responsavel = payload.responsavel

    await db.commit()
    await db.refresh(sol)
    return sol


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