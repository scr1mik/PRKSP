from typing import Protocol


class SessionStore(Protocol):
    def set_user_id(self, session_id: str, user_id: int, ttl_seconds: int) -> None:
        ...

    def get_user_id(self, session_id: str) -> int | None:
        ...

    def delete(self, session_id: str) -> None:
        ...

    def close(self) -> None:
        ...


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, int] = {}

    def set_user_id(self, session_id: str, user_id: int, ttl_seconds: int) -> None:
        self._sessions[session_id] = user_id

    def get_user_id(self, session_id: str) -> int | None:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def close(self) -> None:
        self._sessions.clear()


class RedisSessionStore:
    def __init__(self, redis_url: str) -> None:
        from redis import Redis

        self.redis = Redis.from_url(redis_url, decode_responses=True)

    def set_user_id(self, session_id: str, user_id: int, ttl_seconds: int) -> None:
        self.redis.setex(self._key(session_id), ttl_seconds, str(user_id))

    def get_user_id(self, session_id: str) -> int | None:
        user_id = self.redis.get(self._key(session_id))
        return int(user_id) if user_id else None

    def delete(self, session_id: str) -> None:
        self.redis.delete(self._key(session_id))

    def close(self) -> None:
        self.redis.close()

    @staticmethod
    def _key(session_id: str) -> str:
        return f"session:{session_id}"


def create_session_store(redis_url: str) -> SessionStore:
    if redis_url:
        return RedisSessionStore(redis_url)
    return InMemorySessionStore()
