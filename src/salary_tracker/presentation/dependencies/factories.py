from salary_tracker.domain.sheet.factories import IRateTableFactory
from salary_tracker.domain.sheet.impl.factory.rate_table_factory import RateTableFactory


async def get_rate_table_factory() -> IRateTableFactory:
    return RateTableFactory()