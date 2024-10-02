from uuid import UUID


class DomainException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UserNotFoundDomainException(DomainException):
    def __init__(self, user_uuid: UUID):
        super().__init__(f"User with uuid {user_uuid} not found")
        self.user_uuid = user_uuid


class SheetNotFoundDomainException(DomainException):
    def __init__(self, sheet_uuid: UUID):
        super().__init__(f"Sheet with uuid {sheet_uuid} not found")
        self.sheet_uuid = sheet_uuid