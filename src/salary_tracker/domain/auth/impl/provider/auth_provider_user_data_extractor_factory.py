from pydantic import validate_call

from salary_tracker.domain.auth.factories import IAuthProviderUserDataExtractorFactory
from salary_tracker.domain.auth.models import AuthProvider
from salary_tracker.domain.auth.services import IAuthProviderUserDataExtractor
from salary_tracker.domain.exceptions import DomainException


class AuthProviderUserDataExtractorFactory(IAuthProviderUserDataExtractorFactory):
    @validate_call
    def __init__(self, google_app_client_id: str):
        self._google_app_client_id = google_app_client_id

    def create(self, provider: AuthProvider) -> IAuthProviderUserDataExtractor:
        if provider == AuthProvider.GOOGLE:
            from salary_tracker.domain.auth.impl.provider.google_auth_provider_user_data_extractor import \
                GoogleAuthProviderUserDataExtractor
            return GoogleAuthProviderUserDataExtractor(app_client_id=self._google_app_client_id)
        raise DomainException(f"Unsupported provider: {provider}")
