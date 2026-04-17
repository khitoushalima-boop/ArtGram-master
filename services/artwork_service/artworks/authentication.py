from dataclasses import dataclass

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


@dataclass
class ServiceJWTUser:
    id: int

    @property
    def is_authenticated(self) -> bool:
        return True


class ServiceJWTAuthentication(JWTAuthentication):
    """
    Accept JWTs issued by user-service without requiring a local auth user row.
    """

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")
        if user_id is None:
            raise InvalidToken("Token contained no recognizable user identification")
        return ServiceJWTUser(id=int(user_id))
