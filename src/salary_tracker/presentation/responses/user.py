from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class UserResponse(BaseModel):
    uuid: UUID
    email: EmailStr
    name: str