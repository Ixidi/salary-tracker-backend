from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Awaitable

from typing_extensions import Generic

SuccessType = TypeVar('SuccessType')


class Result(ABC, Generic[SuccessType]):

    @property
    @abstractmethod
    def value(self) -> SuccessType | None:
        pass

    @property
    @abstractmethod
    def error(self) -> Exception | None:
        pass

    @abstractmethod
    def is_success(self) -> bool:
        pass

    @abstractmethod
    def is_failure(self) -> bool:
        pass


class _Success(Result[SuccessType]):
    def __init__(self, value: SuccessType):
        self._value = value

    @property
    def value(self) -> SuccessType | None:
        return self._value

    @property
    def error(self) -> Exception | None:
        return None

    def is_success(self) -> bool:
        return True

    def is_failure(self) -> bool:
        return False


class _Error(Result[SuccessType]):
    def __init__(self, error: Exception):
        self._error = error

    @property
    def value(self) -> SuccessType | None:
        return None

    @property
    def error(self) -> Exception | None:
        return self._error

    def is_success(self) -> bool:
        return False

    def is_failure(self) -> bool:
        return True


def as_result(func: Callable[..., SuccessType]) -> Callable[..., Result[SuccessType]]:
    def wrapper(*args, **kwargs) -> Result[SuccessType]:
        try:
            return _Success(func(*args, **kwargs))
        except Exception as e:
            return _Error(e)

    return wrapper


async def a_as_result(func: Callable[..., Awaitable[SuccessType]]) -> Callable[..., Awaitable[Result[SuccessType]]]:
    async def wrapper(*args, **kwargs) -> Result[SuccessType]:
        try:
            return _Success(await func(*args, **kwargs))
        except Exception as e:
            return _Error(e)

    return wrapper
