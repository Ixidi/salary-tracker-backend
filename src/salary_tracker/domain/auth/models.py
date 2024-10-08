from enum import StrEnum
from uuid import UUID

from asyncpg.pgproto.pgproto import timedelta
from pydantic import AwareDatetime, BaseModel, AnyHttpUrl, EmailStr

from salary_tracker.domain.user.models import User


class TokenSettings(BaseModel):
    access_token_private_key: str
    access_token_expiration_time: timedelta
    access_token_issuer: str
    access_token_audience: str
    refresh_token_expiration_time: timedelta


class AccessToken(BaseModel):
    user_uuid: UUID
    token: str
    expires_at: AwareDatetime


class RefreshToken(BaseModel):
    user_uuid: UUID
    token: str
    expires_at: AwareDatetime


class TokenPair(BaseModel):
    user: User
    access_token: AccessToken
    refresh_token: RefreshToken


class AuthProvider(StrEnum):
    GOOGLE = "google"


class AuthProviderUserData(BaseModel):
    provider: AuthProvider
    email: EmailStr
    external_id: str
    name: str
    avatar: AnyHttpUrl | None


class UserExternalAccount(BaseModel):
    provider: AuthProvider
    user_uuid: UUID
    external_id: str
