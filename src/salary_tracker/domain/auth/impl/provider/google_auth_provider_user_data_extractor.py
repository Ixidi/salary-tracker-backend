from google.auth.transport import requests
from google.oauth2 import id_token
from pydantic import BaseModel

from salary_tracker.domain.auth.models import AuthProviderUserData, AuthProvider
from salary_tracker.domain.auth.services import IAuthProviderUserDataExtractor


class GoogleAuthProviderUserDataExtractor(IAuthProviderUserDataExtractor, BaseModel):
    app_client_id: str

    async def extract_from_token(self, token: str) -> AuthProviderUserData | None:
        try:
            id_info = id_token.verify_oauth2_token(
                id_token=token,
                request=requests.Request(),
                audience=self.app_client_id
            )

            return AuthProviderUserData(
                provider=AuthProvider.GOOGLE,
                email=id_info["email"],
                external_id=id_info["sub"],
                name=id_info["name"],
                avatar=id_info.get("picture", None)
            )
        except ValueError:
            return None
