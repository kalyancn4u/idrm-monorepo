"""
api/v1/services.py — service-request routes (Module M3).

The core lifecycle: create, list, read, plus the status-changing action
sub-endpoints (POST /services/{id}/<action>) — IDRM has no PUT/PATCH/DELETE.
Thin handlers delegate to `services.service_service`. Mounted under `/api/v1`,
so the full paths are `/api/v1/services`, `/api/v1/services/{id}/approve`, etc.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user, get_current_user_optional
from dbmodels.user import User
from schemas.service import (
    AcceptBody,
    ApproveBody,
    CancelBody,
    CompleteBody,
    DisputeBody,
    RejectBody,
    ServiceCreate,
    ServiceListResponse,
    ServiceOut,
    VerifyBody,
)
from services import service_service

router = APIRouter(prefix="/services", tags=["services"])


# ---- create / read ----------------------------------------------------------
@router.post("", status_code=201, response_model=ServiceOut)
async def create_service(
    body: ServiceCreate,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """File a new request for help (the logged-in user becomes the requestor)."""
    return await service_service.create_request(db, current, body)


@router.get("", response_model=ServiceListResponse)
async def list_services(
    status: str | None = None,
    service_type: str | None = None,
    priority: str | None = None,
    mine: bool = False,
    provider_id: uuid.UUID | None = None,
    page: int = 1,
    per_page: int = 20,
    viewer: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> ServiceListResponse:
    """List requests (newest first) with optional status/type/priority filters and
    pagination. Public-safe: compact rows with no requestor identity.

    `mine=true` returns only the signed-in user's own requests (requires auth — 401
    otherwise); `provider_id=<org>` returns a provider org's assigned requests (the
    provider pages). These power the respective dashboards.
    """
    requestor_id = None
    if mine:
        if viewer is None:
            raise HTTPException(status_code=401, detail="Authentication required for mine=true")
        requestor_id = viewer.user_id
    data = await service_service.list_requests(
        db,
        status=status,
        service_type=service_type,
        priority=priority,
        requestor_id=requestor_id,
        provider_id=provider_id,
        page=page,
        per_page=per_page,
    )
    return ServiceListResponse(data=data)


@router.get("/{service_id}", response_model=ServiceOut)
async def get_service(
    service_id: uuid.UUID,
    viewer: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """Read one request. Identity/contact are redacted unless the viewer is the
    requestor or a privileged role (privacy levels PUBLIC/PROTECTED/PRIVATE)."""
    return await service_service.get_request(db, service_id, viewer)


# ---- lifecycle actions ------------------------------------------------------
@router.post("/{service_id}/approve", response_model=ServiceOut)
async def approve_service(
    service_id: uuid.UUID,
    body: ApproveBody,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """DM Authority approves a SUBMITTED request."""
    return await service_service.approve(db, current, service_id, body)


@router.post("/{service_id}/reject", response_model=ServiceOut)
async def reject_service(
    service_id: uuid.UUID,
    body: RejectBody,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """DM Authority rejects a SUBMITTED (or DISPUTED) request, with a reason."""
    return await service_service.reject(db, current, service_id, body)


@router.post("/{service_id}/accept", response_model=ServiceOut)
async def accept_service(
    service_id: uuid.UUID,
    body: AcceptBody,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """Provider accepts an APPROVED request on behalf of an organization."""
    return await service_service.accept(db, current, service_id, body)


@router.post("/{service_id}/start", response_model=ServiceOut)
async def start_service(
    service_id: uuid.UUID,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """Provider starts work: ACCEPTED → IN_PROGRESS."""
    return await service_service.start(db, current, service_id)


@router.post("/{service_id}/complete", response_model=ServiceOut)
async def complete_service(
    service_id: uuid.UUID,
    body: CompleteBody,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """Provider marks the service delivered: IN_PROGRESS → COMPLETED."""
    return await service_service.complete(db, current, service_id, body)


@router.post("/{service_id}/verify", response_model=ServiceOut)
async def verify_service(
    service_id: uuid.UUID,
    body: VerifyBody,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """Requestor confirms completion with a 1–5 rating: COMPLETED → VERIFIED."""
    return await service_service.verify(db, current, service_id, body)


@router.post("/{service_id}/cancel", response_model=ServiceOut)
async def cancel_service(
    service_id: uuid.UUID,
    body: CancelBody,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """Requestor cancels while SUBMITTED/APPROVED → CANCELLED."""
    return await service_service.cancel(db, current, service_id, body)


@router.post("/{service_id}/dispute", response_model=ServiceOut)
async def dispute_service(
    service_id: uuid.UUID,
    body: DisputeBody,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceOut:
    """Requestor raises a dispute from IN_PROGRESS/COMPLETED → DISPUTED."""
    return await service_service.dispute(db, current, service_id, body)
