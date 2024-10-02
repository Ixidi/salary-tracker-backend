import secrets
from datetime import timedelta, datetime, UTC
from uuid import UUID, uuid4

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from jose import jwt, JWTError

from salary_tracker.domain.auth.models import RefreshToken, TokenPair, AccessToken
from salary_tracker.domain.auth.repositories import IRefreshTokenRepository
from salary_tracker.domain.auth.services import ITokenService


class TokenService(ITokenService):
    def __init__(self,
                 access_token_private_key: str,
                 access_token_expiration_time: timedelta,
                 access_token_issuer: str,
                 access_token_audience: str,
                 refresh_token_expiration_time: timedelta,
                 refresh_token_repository: IRefreshTokenRepository
                 ):
        self.private_key = serialization.load_pem_private_key(
            access_token_private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

        self.private_key_str = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        self.public_key_str = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        self.access_token_expiration_time = access_token_expiration_time
        self.access_token_issuer = access_token_issuer
        self.access_token_audience = access_token_audience
        self.refresh_token_expiration_time = refresh_token_expiration_time

        self.refresh_token_repository = refresh_token_repository

    async def validate_access_token(self, access_token: str) -> AccessToken | None:
        try:
            claims = jwt.decode(
                token=access_token,
                key=self.public_key_str,
                algorithms=['RS256'],
                audience=self.access_token_audience,
                issuer=self.access_token_issuer
            )

            return AccessToken(
                user_uuid=UUID(claims['sub']),
                token=access_token,
                expires_at=datetime.fromtimestamp(claims['exp'], tz=UTC)
            )
        except JWTError as e:
            return None

    async def validate_refresh_token(self, refresh_token: str) -> RefreshToken | None:
        return await self.refresh_token_repository.get_by_token(refresh_token)

    async def create_token_pair(self, user_uuid: UUID, user_agent: str) -> TokenPair:
        now = datetime.now(tz=UTC)
        expiration_time = now + self.access_token_expiration_time

        claims = {
            'sub': f'{user_uuid}',
            'iat': now,
            'exp': expiration_time,
            'jti': str(uuid4()),
            'aud': self.access_token_audience,
            'iss': self.access_token_issuer
        }

        token = jwt.encode(claims, self.private_key_str, algorithm='RS256')

        access_token = AccessToken(
            user_uuid=user_uuid,
            token=token,
            expires_at=expiration_time
        )

        refresh_token = RefreshToken(
            user_uuid=user_uuid,
            token=secrets.token_urlsafe(128),
            expires_at=datetime.now(tz=UTC) + self.refresh_token_expiration_time,
            user_agent=user_agent
        )

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def save_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        return await self.refresh_token_repository.upsert(refresh_token)

    async def delete_refresh_token(self, refresh_token: str) -> None:
        await self.refresh_token_repository.delete(refresh_token)
