class UseCaseException(Exception):
    def __init__(self, message: str, key: str):
        self.message = message
        self.key = key
        super().__init__(message)


class AuthException(UseCaseException):
    def __init__(self, message: str):
        super().__init__(message, "auth_error")


class DomainRuleException(UseCaseException):
    def __init__(self, message: str):
        super().__init__(message, "core.domain_error")


class PermissionDeniedException(UseCaseException):
    def __init__(self, message: str):
        super().__init__(f"Permission denied: {message}", "core.permission_denied")


class SheetTitleDoesNotMatchException(UseCaseException):
    def __init__(self, message: str):
        super().__init__(message, "core.sheet_title_does_not_match")
