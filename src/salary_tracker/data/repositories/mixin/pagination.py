from abc import ABC, abstractmethod
from typing import TypeVar, Type

from pydantic import BaseModel, validate_call, ConfigDict
from sqlalchemy import select, Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Generic

from salary_tracker.data.model import Base
from salary_tracker.domain.pagination import PaginatedRequest, PaginatedResult

DatabaseModelType = TypeVar("DatabaseModelType", bound=Base)
DataType = TypeVar("DataType", bound=BaseModel)
FiltersType = TypeVar("FiltersType")


class GetPaginatedMixin(Generic[DatabaseModelType, DataType, FiltersType], ABC):
    _model: Type[DatabaseModelType]

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    def _apply_pagination_filters(self, query: Select, filters: FiltersType) -> Select:
        pass

    @abstractmethod
    def _map_to_domain(self, db_result: DatabaseModelType) -> DataType:
        pass

    async def _get_paginated(self, request: PaginatedRequest[FiltersType]) -> PaginatedResult[DataType]:
        session = self.session
        query = self._apply_pagination_filters(select(self._model), request.filters)

        page_params = request.page_params
        items = await session.execute(
            query.offset(page_params.page * page_params.per_page).limit(page_params.per_page)
        )

        total_count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await session.execute(total_count_query)
        total = total_count_result.scalar()

        return PaginatedResult(
            items=[self._map_to_domain(db_result=x) for x in items.scalars()],
            total=total,
            page=page_params.page,
            per_page=page_params.per_page,
            total_pages=(total // page_params.per_page) + (1 if total % page_params.per_page else 0)
        )
