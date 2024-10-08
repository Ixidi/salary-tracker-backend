from abc import ABC, abstractmethod

from salary_tracker.domain.auth.models import AuthProvider
from salary_tracker.domain.auth.services import IAuthProviderUserDataExtractor


class IAuthProviderUserDataExtractorFactory(ABC):

    @abstractmethod
    def create(self, provider: AuthProvider) -> IAuthProviderUserDataExtractor:
        pass
