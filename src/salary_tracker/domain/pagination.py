from typing import TypeVar, Generic

from pydantic import BaseModel, conint

DataType = TypeVar("DataType", bound=BaseModel)
FiltersType = TypeVar("FiltersType")


class PageParams(BaseModel):
    page: conint(ge=0)
    per_page: conint(ge=1, le=100)


class PaginatedRequest(BaseModel, Generic[FiltersType]):
    page_params: PageParams
    filters: FiltersType


class PaginatedResult(BaseModel, Generic[DataType]):
    items: list[DataType]
    total: int
    page: int
    per_page: int
    total_pages: int
