import dataclasses

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

    def get_payload(self, encoded_token: str) -> JWTToken:
        raise NotImplementedError
