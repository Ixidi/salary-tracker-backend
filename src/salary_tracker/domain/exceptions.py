from uuid import UUID

from pydantic_core import ValidationError


class DomainException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ModelValidationDomainException(DomainException):
    def __init__(self, validation_error: ValidationError):
        super().__init__(str(validation_error.errors()[0]["msg"]))


class UserNotFoundDomainException(DomainException):
    def __init__(self, user_uuid: UUID):
        super().__init__(f"User with uuid {user_uuid} not found")
        self.user_uuid = user_uuid


class SheetNotFoundDomainException(DomainException):
    def __init__(self, sheet_uuid: UUID):
        super().__init__(f"Sheet with uuid {sheet_uuid} not found")
        self.sheet_uuid = sheet_uuid


class RecordNotFoundDomainException(DomainException):
    def __init__(self, record_uuid: UUID):
        super().__init__(f"Record with uuid {record_uuid} not found")
        self.record_uuid = record_uuid


class InvalidTokenDomainException(DomainException):
    def __init__(self):
        super().__init__("Invalid token")


class TokenExpiredDomainException(InvalidTokenDomainException):
    pass