from pydantic import BaseModel, AwareDatetime

from salary_tracker.presentation.responses.user import UserResponse


class AccessTokenResponse(BaseModel):
    token: str
    expires_at: AwareDatetime


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: AccessTokenResponse
