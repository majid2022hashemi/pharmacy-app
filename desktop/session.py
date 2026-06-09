class Session:
    _token: str | None = None
    _user: dict | None = None

    @classmethod
    def set(cls, token: str, user: dict):
        cls._token = token
        cls._user = user

    @classmethod
    def clear(cls):
        cls._token = None
        cls._user = None

    @classmethod
    def token(cls) -> str | None:
        return cls._token

    @classmethod
    def user(cls) -> dict | None:
        return cls._user

    @classmethod
    def has_permission(cls, permission: str) -> bool:
        if cls._user is None:
            return False
        return permission in cls._user.get("permissions", [])

    @classmethod
    def role(cls) -> str | None:
        if cls._user is None:
            return None
        return cls._user.get("role")

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._token is not None
