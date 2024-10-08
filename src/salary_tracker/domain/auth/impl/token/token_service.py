import secrets
from datetime import datetime, UTC
from uuid import UUID, uuid4

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import jwt, JWTError
from pydantic import validate_call, ConfigDict

from salary_tracker.domain.auth.models import RefreshToken, TokenPair, AccessToken, TokenSettings
from salary_tracker.domain.auth.repositories import IRefreshTokenRepository
from salary_tracker.domain.auth.services import ITokenService
from salary_tracker.domain.exceptions import DomainException, TokenExpiredDomainException, UserNotFoundDomainException, \
    InvalidTokenDomainException
from salary_tracker.domain.user.repositories import IUserRepository
from salary_tracker.usecase.exceptions import AuthException


class TokenService(ITokenService):
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, token_settings: TokenSettings, refresh_token_repository: IRefreshTokenRepository,
                 user_repository: IUserRepository):
        self._private_key = serialization.load_pem_private_key(
            token_settings.access_token_private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

        self._private_key_str = self._private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        self._public_key_str = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        self._access_token_expiration_time = token_settings.access_token_expiration_time
        self._access_token_issuer = token_settings.access_token_issuer
        self._access_token_audience = token_settings.access_token_audience
        self._refresh_token_expiration_time = token_settings.refresh_token_expiration_time

        self._refresh_token_repository = refresh_token_repository
        self._user_repository = user_repository

    async def validate_access_token(self, access_token: str) -> AccessToken | None:
        try:
            claims = jwt.decode(
                token=access_token,
                key=self._public_key_str,
                algorithms=['RS256'],
                audience=self._access_token_audience,
                issuer=self._access_token_issuer
            )

            return AccessToken(
                user_uuid=UUID(claims['sub']),
                token=access_token,
                expires_at=datetime.fromtimestamp(claims['exp'], tz=UTC)
            )
        except JWTError as e:
            raise InvalidTokenDomainException()

    async def validate_refresh_token(self, refresh_token: str) -> RefreshToken | None:
        return await self._refresh_token_repository.get_by_token(refresh_token)

    async def create_token_pair(self, user_uuid: UUID) -> TokenPair:
        user = await self._user_repository.get_by_uuid(user_uuid)
        if user is None:
            raise UserNotFoundDomainException(user_uuid)

        now = datetime.now(tz=UTC)
        expiration_time = now + self._access_token_expiration_time

        claims = {
            'sub': f'{user_uuid}',
            'iat': now,
            'exp': expiration_time,
            'jti': str(uuid4()),
            'aud': self._access_token_audience,
            'iss': self._access_token_issuer
        }

        token = jwt.encode(claims, self._private_key_str, algorithm='RS256')

        access_token = AccessToken(
            user_uuid=user_uuid,
            token=token,
            expires_at=expiration_time
        )

        refresh_token = RefreshToken(
            user_uuid=user_uuid,
            token=secrets.token_urlsafe(128),
            expires_at=now + self._refresh_token_expiration_time
        )

        await self._refresh_token_repository.insert(refresh_token)

        return TokenPair(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def rotate_refresh_token(self, refresh_token: str) -> TokenPair:
        old_refresh_token = await self._refresh_token_repository.get_by_token(refresh_token)
        if old_refresh_token is None:
            raise InvalidTokenDomainException()

        if old_refresh_token.expires_at < datetime.now(tz=UTC):
            raise TokenExpiredDomainException()

        await self._refresh_token_repository.delete(old_refresh_token.token)

        return await self.create_token_pair(old_refresh_token.user_uuid)

    async def delete_refresh_token(self, refresh_token: str) -> None:
        await self._refresh_token_repository.delete(refresh_token)
