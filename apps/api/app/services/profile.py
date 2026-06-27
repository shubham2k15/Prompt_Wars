from sqlalchemy.orm import Session

from ..models import User, UserProfile
from ..schemas import ProfileResponse, ProfileUpdateRequest


def get_or_create_profile(db: Session, user: User) -> UserProfile:
    profile = user.profile
    if profile:
        return profile
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def build_profile_response(user: User, profile: UserProfile) -> ProfileResponse:
    return ProfileResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=profile.full_name,
        exam_type=profile.exam_type,
        target_rank=profile.target_rank,
        preferred_language=profile.preferred_language,
        motivation_style=profile.motivation_style,
        communication_style=profile.communication_style,
        study_schedule=profile.study_schedule or {},
        wellness_preferences=profile.wellness_preferences or {},
    )


def update_profile(db: Session, user: User, payload: ProfileUpdateRequest) -> ProfileResponse:
    profile = get_or_create_profile(db, user)
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return build_profile_response(user, profile)

