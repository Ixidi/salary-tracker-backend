from functools import lru_cache

from salary_tracker.presentation.settings import AppSettings

@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()