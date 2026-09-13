import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.settings import settings
from app.middleware.auth import get_current_user
from app.models.collaboration import Collaboration, CollaborationInvitation, CollaborationMember
from app.models.user import User
from app.schemas.collaboration import (
    CollaborationCreate,
    CollaborationMemberResponse,
    CollaborationResponse,
    InvitationCreate,
    InvitationDetails,
    InvitationResponse,
)

router = APIRouter()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_owned_collaboration(collaboration_id: int, user: User, db: Session) -> Collaboration:
    collaboration = db.query(Collaboration).filter(
        Collaboration.id == collaboration_id,
        Collaboration.owner_id == user.id,
    ).first()
    if not collaboration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found")
    return collaboration


@router.get("", response_model=list[CollaborationResponse])
async def list_collaborations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    owned = db.query(Collaboration).filter(Collaboration.owner_id == current_user.id).all()
    member_ids = db.query(CollaborationMember.collaboration_id).filter(
        CollaborationMember.user_id == current_user.id
    ).all()
    joined = db.query(Collaboration).filter(
        Collaboration.id.in_([item[0] for item in member_ids])
    ).all() if member_ids else []
    return owned + [collaboration for collaboration in joined if collaboration.id not in {item.id for item in owned}]


@router.post("", response_model=CollaborationResponse, status_code=status.HTTP_201_CREATED)
async def create_collaboration(
    payload: CollaborationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collaboration = Collaboration(name=payload.name.strip(), owner_id=current_user.id)
    db.add(collaboration)
    db.commit()
    db.refresh(collaboration)
    return collaboration


@router.post("/{collaboration_id}/invitations", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    collaboration_id: int,
    payload: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collaboration = get_owned_collaboration(collaboration_id, current_user, db)
    invitee_email = str(payload.email).lower()
    if invitee_email == current_user.email.lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot invite yourself")

    raw_token = secrets.token_urlsafe(32)
    invitation = CollaborationInvitation(
        collaboration_id=collaboration.id,
        inviter_id=current_user.id,
        invitee_email=invitee_email,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invitation)
    db.commit()
    return InvitationResponse(
        collaboration_id=collaboration.id,
        collaboration_name=collaboration.name,
        invitee_email=invitee_email,
        invite_url=f"{settings.FRONTEND_URL}/collaborations/accept?token={raw_token}",
        expires_at=invitation.expires_at,
    )


def get_invitation(token: str, db: Session) -> CollaborationInvitation:
    invitation = db.query(CollaborationInvitation).filter(
        CollaborationInvitation.token_hash == hash_token(token)
    ).first()
    if not invitation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    if invitation.accepted_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation has already been accepted")
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation has expired")
    return invitation


@router.get("/invitations/{token}", response_model=InvitationDetails)
async def invitation_details(token: str, db: Session = Depends(get_db)):
    invitation = get_invitation(token, db)
    return InvitationDetails(
        collaboration_id=invitation.collaboration_id,
        collaboration_name=invitation.collaboration.name,
        invitee_email=invitation.invitee_email,
        expires_at=invitation.expires_at,
        accepted=False,
    )


@router.post("/invitations/{token}/accept", response_model=CollaborationMemberResponse)
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    invitation = get_invitation(token, db)
    if current_user.email.lower() != invitation.invitee_email.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sign in with the invited email address")

    member = CollaborationMember(
        collaboration_id=invitation.collaboration_id,
        user_id=current_user.id,
    )
    invitation.accepted_at = datetime.now(timezone.utc)
    db.add(member)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already a collaborator")
    return CollaborationMemberResponse(
        user_id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        joined_at=member.joined_at,
    )


@router.get("/{collaboration_id}/members", response_model=list[CollaborationMemberResponse])
async def list_members(
    collaboration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    collaboration = db.query(Collaboration).filter(Collaboration.id == collaboration_id).first()
    if not collaboration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration not found")
    is_member = db.query(CollaborationMember).filter(
        CollaborationMember.collaboration_id == collaboration_id,
        CollaborationMember.user_id == current_user.id,
    ).first()
    if collaboration.owner_id != current_user.id and not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a collaborator")
    members = db.query(CollaborationMember, User).join(User, User.id == CollaborationMember.user_id).filter(
        CollaborationMember.collaboration_id == collaboration_id
    ).all()
    return [CollaborationMemberResponse(user_id=user.id, email=user.email, username=user.username, joined_at=member.joined_at)
            for member, user in members]