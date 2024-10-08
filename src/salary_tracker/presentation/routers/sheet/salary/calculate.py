from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import AwareDatetime

from salary_tracker.presentation.dependencies.auth import get_current_user_uuid
from salary_tracker.presentation.dependencies.usecases import get_calculate_salary_use_case
from salary_tracker.presentation.responses.salary import SalaryResponse
from salary_tracker.usecase.sheet.salary.calculate_salary import CalculateSalaryUseCase

router = APIRouter()


@router.get(
    "/{sheet_uuid}/salary/",
    description="Calculate salary for a sheet",
    response_model=SalaryResponse
)
async def calculate_salary(
        sheet_uuid: UUID,
        datetime_from: AwareDatetime,
        datetime_to: AwareDatetime,
        current_user_uuid: UUID = Depends(get_current_user_uuid),
        calculate_salary_use_case: CalculateSalaryUseCase = Depends(get_calculate_salary_use_case)
):
    return await calculate_salary_use_case(sheet_uuid, current_user_uuid, datetime_from, datetime_to)