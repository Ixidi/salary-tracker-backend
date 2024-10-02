from uuid import UUID


class UseCaseException(Exception):
    def __init__(self, message: str, key: str):
        self.message = message
        self.key = key
        super().__init__(message)

class UserNotFoundException(UseCaseException):
    def __init__(self, user_uuid: UUID):
        super().__init__(f"User with uuid {user_uuid} not found", "user.not_found")
        self.user_uuid = user_uuid

class InvalidTokenException(UseCaseException):
    def __init__(self):
        super().__init__("Invalid token", "auth.invalid_token")