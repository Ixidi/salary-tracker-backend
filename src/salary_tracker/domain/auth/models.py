from enum import StrEnum
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, AnyHttpUrl, EmailStr


class AccessToken(BaseModel):
    user_uuid: UUID
    token: str
    expires_at: AwareDatetime


class RefreshToken(BaseModel):
    user_uuid: UUID
    token: str
    user_agent: str
    expires_at: AwareDatetime


class TokenPair(BaseModel):
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
