from __future__ import annotations

from redis import Redis


class RedisManager:
    """
    Centralized Redis connection manager.

    Redis is intentionally treated as an auxiliary infrastructure
    component. MySQL remains the authoritative persistent data store.
    """

    def __init__(
        self,
        redis_url: str,
        *,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        decode_responses: bool = True,
    ) -> None:
        self.client: Redis[str] = Redis.from_url(
            redis_url,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=decode_responses,
        )

    def ping(self) -> bool:
        """
        Verify that Redis is reachable.
        """
        return bool(self.client.ping())

    def get(self, key: str) -> str | None:
        """
        Retrieve a value.
        """
        return self.client.get(key)

    def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool:
        """
        Store a value.

        nx=True is useful for atomic lock acquisition.
        """
        result = self.client.set(
            name=key,
            value=value,
            ex=ex,
            nx=nx,
        )

        return bool(result)

    def delete(self, key: str) -> int:
        """
        Delete a Redis key.
        """
        return int(self.client.delete(key))

    def exists(self, key: str) -> bool:
        """
        Check whether a key exists.
        """
        return bool(self.client.exists(key))

    def expire(self, key: str, seconds: int) -> bool:
        """
        Set or replace a key expiration.
        """
        return bool(self.client.expire(key, seconds))

    def close(self) -> None:
        """
        Close the Redis connection pool.
        """
        self.client.close()

    def raw(self) -> Redis[str]:
        """
        Return the underlying Redis client.

        This should only be used by infrastructure-level services that
        require Redis functionality not exposed by this manager.
        """
        return self.client