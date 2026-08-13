from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.security import Actor, get_current_actor, revoke_token
from app.services import AuthService

router = APIRouter(prefix="/auth", tags=["身份认证"])


class CaptchaChallenge(BaseModel):
    provider: str
    captcha_id: str
    expires_in: int
    track_length: int | None = None
    canvas_width: int | None = None
    canvas_height: int | None = None
    puzzle_offset: int | None = None
    app_id: str | None = None


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    captcha_id: str = Field(min_length=1)
    slider_position: int | None = Field(default=None, ge=0, le=1000)
    captcha_ticket: str | None = Field(default=None, min_length=1)
    captcha_randstr: str | None = Field(default=None, min_length=1)


class UserProfile(BaseModel):
    username: str
    display_name: str
    tenant_id: str
    property_ids: list[str]
    roles: list[str]


class SessionResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfile


auth_service = AuthService()
CurrentActor = Annotated[Actor, Depends(get_current_actor)]


@router.post("/captcha", response_model=CaptchaChallenge, summary="创建登录滑块挑战")
def create_captcha() -> CaptchaChallenge:
    try:
        return CaptchaChallenge(**auth_service.create_captcha())
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
        ) from error


@router.post("/login", response_model=SessionResponse, summary="校验滑块并创建登录会话")
def login(payload: LoginRequest) -> SessionResponse:
    try:
        return SessionResponse(**auth_service.login(payload.model_dump()))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error


@router.get("/me", response_model=UserProfile, summary="读取当前登录身份")
def me(actor: CurrentActor) -> UserProfile:
    profile = auth_service.profile_for(actor)
    return UserProfile(**profile)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="注销当前登录会话")
def logout(actor: CurrentActor) -> None:
    revoke_token(actor)
