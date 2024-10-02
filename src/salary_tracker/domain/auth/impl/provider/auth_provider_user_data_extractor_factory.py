from pydantic import BaseModel

from salary_tracker.domain.auth.models import AuthProvider
from salary_tracker.domain.auth.services import IAuthProviderUserDataExtractor, IAuthProviderUserDataExtractorFactory


class AuthProviderUserDataExtractorFactory(IAuthProviderUserDataExtractorFactory, BaseModel):
    google_app_client_id: str

    def create(self, provider: AuthProvider) -> IAuthProviderUserDataExtractor:
        if provider == AuthProvider.GOOGLE:
            from salary_tracker.domain.auth.impl.provider.google_auth_provider_user_data_extractor import \
                GoogleAuthProviderUserDataExtractor
            return GoogleAuthProviderUserDataExtractor(app_client_id=self.google_app_client_id)
        raise ValueError(f"Unsupported provider: {provider}")
