from fastapi import APIRouter, Depends

from app.interfaces.rest.deps.user import get_current_user
from app.domain.entities.user import User
from app.interfaces.rest.schemas.auth_schema import UserResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id.value,
        email=current_user.email.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
