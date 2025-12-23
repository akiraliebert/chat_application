from fastapi import APIRouter, Depends, HTTPException, status

from app.interfaces.rest.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.interfaces.rest.deps.user import (
    get_user_repository,
    get_password_hasher,
    get_jwt_service
)
from app.interfaces.rest.deps.common import get_uow

from app.application.use_cases.user.register_user import RegisterUserUseCase
from app.application.use_cases.user.login_user import (
    LoginUserUseCase,
    InvalidCredentialsError,
    InactiveUserError,
)
from app.application.exceptions import EmailAlreadyExistsError
from app.application.security.jwt_service import JWTService

from app.infrastructure.security.jwt_service import JWTErrorInvalidToken


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    uow=Depends(get_uow),
    user_repo=Depends(get_user_repository),
    password_hasher=Depends(get_password_hasher),
):
    use_case = RegisterUserUseCase(
        uow=uow,
        user_repository=user_repo,
        password_hasher=password_hasher,
    )

    try:
        user = await use_case.execute(
            email=data.email,
            raw_password=data.password,
        )
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    return UserResponse(
        id=user.id.value,
        email=user.email.value,
        is_active=user.is_active,
        is_online=user.is_online,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    uow=Depends(get_uow),
    user_repo=Depends(get_user_repository),
    password_hasher=Depends(get_password_hasher),
    jwt_service: JWTService = Depends(get_jwt_service),
):
    use_case = LoginUserUseCase(
        uow=uow,
        user_repository=user_repo,
        password_hasher=password_hasher,
    )

    try:
        user = await use_case.execute(
            email=data.email,
            raw_password=data.password,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    return TokenResponse(
        access_token=jwt_service.create_access_token(user.id.value),
        refresh_token=jwt_service.create_refresh_token(user.id.value),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    jwt_service: JWTService = Depends(get_jwt_service),
):
    try:
        user_id = jwt_service.verify_refresh_token(data.refresh_token)
    except JWTErrorInvalidToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return TokenResponse(
        access_token=jwt_service.create_access_token(user_id),
        refresh_token=jwt_service.create_refresh_token(user_id),
    )
