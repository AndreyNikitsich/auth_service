import dataclasses
import uuid
from datetime import datetime, timezone, timedelta

from jose import JWSError, JWTError, jws, jwt

from entities.tokens import JWTToken

from .exceptions import ExpiredTokenError, InvalidTokenSignatureError


@dataclasses.dataclass
class BaseTokenService:
    secret_key: str
    algorithm: str
    expires_delta_minutes: int

    async def validate_token(self, encoded_token: str):
        try:
            jws.verify(encoded_token, self.secret_key, self.algorithm)
        except JWSError as e:
            raise InvalidTokenSignatureError from e

        try:
            jwt.decode(encoded_token, self.secret_key, self.algorithm)
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
