from datetime import timedelta
from typing import Literal

from pydantic import PostgresDsn, AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    root_path: str
    cors_allow_origins: frozenset[AnyHttpUrl]

    database_url: PostgresDsn

    access_token_private_key: str
    access_token_expiration_time: timedelta
    access_token_issuer: str
    access_token_audience: str
    refresh_token_expiration_time: timedelta

    google_app_client_id: str

    refresh_token_cookie_path: str
    refresh_token_cookie_http_only: bool
    refresh_token_cookie_same_site: Literal['strict', 'lax', 'none']
    refresh_token_cookie_domain: str
    refresh_token_cookie_secure: bool

    model_config = ConfigDict(frozen=True)
