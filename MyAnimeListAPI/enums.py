from enum import Enum


class CustomBaseEnum(Enum):
    def __str__(self) -> str:
        return self.value


class Scopes(CustomBaseEnum):
    USER_WRITE = "user:write"


class TokenType(CustomBaseEnum):
    BEARER = "Authorization"
    API_KEY = "X-MAL-CLIENT-ID"
