from typing import Any

from pydantic import BaseModel
from typing_extensions import TypeVar, Generic

from salary_tracker.domain.pagination import PaginatedResult

DataType = TypeVar("DataType", bound=BaseModel)

class PaginatedResultResponse(PaginatedResult[DataType]):
    pass
