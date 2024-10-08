from uuid import UUID

from pydantic import EmailStr, BaseModel


class User(BaseModel):
    uuid: UUID
    name: str
    email: EmailStr


class NewUserData(BaseModel):
    name: str
    email: EmailStr
