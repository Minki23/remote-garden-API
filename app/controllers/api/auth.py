from app.core.dependencies import AuthServiceDep
from app.models.dtos.google_login import GoogleLoginDTO
from fastapi import APIRouter
from app.models.dtos.auth import RefreshTokenDTO, TokenDTO

router = APIRouter()


@router.post("/login/google", response_model=TokenDTO)
async def google_login(payload: GoogleLoginDTO, auth_service: AuthServiceDep):
    return await auth_service.login_with_google(payload.id_token)


@router.post("/refresh", response_model=TokenDTO)
async def refresh(payload: RefreshTokenDTO, auth_service: AuthServiceDep):
    return await auth_service.refresh(payload.refresh_token)
