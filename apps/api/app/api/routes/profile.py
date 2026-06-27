from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import get_current_user
from ...models import User
from ...schemas import ProfileResponse, ProfileUpdateRequest
from ...services.profile import build_profile_response, get_or_create_profile, update_profile


router = APIRouter()


@router.get("", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ProfileResponse:
    profile = get_or_create_profile(db, current_user)
    return build_profile_response(current_user, profile)


@router.patch("", response_model=ProfileResponse)
def patch_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    return update_profile(db, current_user, payload)

