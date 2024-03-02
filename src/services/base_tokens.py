import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jose import JWSError, JWTError, jws, jwt

from entities.tokens import JWTToken

from .exceptions import ExpiredTokenError, InvalidTokenSignatureError


@dataclass
class BaseTokenService:
    secret_key: str
    public_key: str | None
    algorithm: str
    expires_delta_minutes: int

    async def validate_token(self, encoded_token: str):
        decode_key = self.secret_key if self.public_key is None else self.public_key

        try:
            jws.verify(encoded_token, decode_key, self.algorithm)
        except JWSError as e:
            raise InvalidTokenSignatureError from e

        try:
            jwt.decode(encoded_token, decode_key, self.algorithm)
        except JWTError as e:
            raise ExpiredTokenError from e

    def _generate_token(self, extra_payload: dict) -> str:
        issued_at = datetime.now(timezone.utc)
        expire = issued_at + timedelta(minutes=self.expires_delta_minutes)

        to_encode = {
            "jti": str(uuid.uuid4()),
            "iat": issued_at,
            "exp": expire,
            **extra_payload,
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def get_payload(self, encoded_token: str) -> JWTToken:
        raise NotImplementedError
