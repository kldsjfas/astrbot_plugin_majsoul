import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import aiohttp

from .models import DataFormatError, PlayerCandidate, PlayerStats


class InvalidNickname(ValueError):
    """Raised when a nickname cannot be queried safely."""


class PlayerNotFound(LookupError):
    """Raised when no matching player exists."""


class MultiplePlayersFound(LookupError):
    """Raised when a partial nickname matches multiple players."""

    def __init__(self, candidates: tuple[str, ...]):
        super().__init__("Multiple players found")
        self.candidates = candidates


class RemoteServiceError(RuntimeError):
    """Raised when the remote API cannot complete a request."""


@dataclass(slots=True)
class _CacheEntry:
    value: PlayerStats
    expires_at: float


class MajsoulApiClient:
    BASE_URL = "https://5-data.amae-koromo.com/api/v2/pl4"
    MODE_QUERY = "16,15,12,11,9,8"
    START_TIME = 1262304000000
    END_TIME = 2147483647000

    def __init__(
        self,
        *,
        timeout: int = 15,
        cache_ttl: int = 600,
        max_cache_entries: int = 256,
    ):
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.max_cache_entries = max_cache_entries
        self._session: aiohttp.ClientSession | None = None
        self._cache: OrderedDict[str, _CacheEntry] = OrderedDict()
        self._inflight: dict[str, asyncio.Task[PlayerStats]] = {}

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None

    async def query_player(self, nickname: str) -> PlayerStats:
        nickname = self._normalize_nickname(nickname)
        key = nickname.casefold()
        cached = self._get_cached(key)
        if cached:
            return cached

        task = self._inflight.get(key)
        if task is None:
            task = asyncio.create_task(self._query_and_cache(key, nickname))
            self._inflight[key] = task
        try:
            return await task
        finally:
            if self._inflight.get(key) is task and task.done():
                self._inflight.pop(key, None)

    async def _query_and_cache(self, key: str, nickname: str) -> PlayerStats:
        candidates = await self.search_players(nickname)
        player = self._select_player(nickname, candidates)
        stats = await self.fetch_stats(player)
        if stats.count <= 0:
            raise PlayerNotFound
        self._set_cached(key, stats)
        return stats

    async def search_players(self, nickname: str) -> list[PlayerCandidate]:
        url = f"{self.BASE_URL}/search_player/{quote(nickname, safe='')}"
        payload = await self._request_json(url)
        if not isinstance(payload, list):
            raise DataFormatError("Invalid search response")

        candidates = []
        for item in payload:
            try:
                candidates.append(PlayerCandidate.from_payload(item))
            except DataFormatError:
                continue
        if not candidates:
            raise PlayerNotFound
        return candidates

    async def fetch_stats(self, player: PlayerCandidate) -> PlayerStats:
        url = (
            f"{self.BASE_URL}/player_stats/{player.account_id}/"
            f"{self.START_TIME}/{self.END_TIME}?mode={self.MODE_QUERY}"
        )
        payload = await self._request_json(url)
        return PlayerStats.from_payload(player.nickname, payload)

    async def _request_json(self, url: str) -> Any:
        session = await self._get_session()
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        try:
                            return await response.json(content_type=None)
                        except (ValueError, TypeError) as exc:
                            raise DataFormatError("Invalid JSON response") from exc

                    if response.status not in {429, 500, 502, 503, 504}:
                        raise RemoteServiceError(
                            f"Remote service returned HTTP {response.status}"
                        )
                    last_error = RemoteServiceError(
                        f"Remote service returned HTTP {response.status}"
                    )
                    retry_after = response.headers.get("Retry-After", "")
                    delay = self._retry_delay(attempt, retry_after)
            except (TimeoutError, aiohttp.ClientError) as exc:
                last_error = exc
                delay = self._retry_delay(attempt)

            if attempt < 2:
                await asyncio.sleep(delay)

        raise RemoteServiceError("Remote service is unavailable") from last_error

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self.timeout, connect=min(5, self.timeout)
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "User-Agent": "AstrBot-Majsoul-Plugin/2.0.1",
                    "Referer": "https://amae-koromo.com/",
                },
            )
        return self._session

    @staticmethod
    def _normalize_nickname(nickname: str) -> str:
        if not isinstance(nickname, str):
            raise InvalidNickname("玩家昵称格式不正确。")
        value = nickname.strip()
        if not value:
            raise InvalidNickname("请输入玩家昵称。")
        if len(value) > 64 or any(ord(char) < 32 for char in value):
            raise InvalidNickname("玩家昵称过长或包含无效字符。")
        return value

    @staticmethod
    def _select_player(
        nickname: str, candidates: list[PlayerCandidate]
    ) -> PlayerCandidate:
        exact = [
            player
            for player in candidates
            if player.nickname.casefold() == nickname.casefold()
        ]
        if exact:
            return exact[0]
        if len(candidates) == 1:
            return candidates[0]
        names = tuple(dict.fromkeys(player.nickname for player in candidates[:5]))
        raise MultiplePlayersFound(names)

    @staticmethod
    def _retry_delay(attempt: int, retry_after: str = "") -> float:
        try:
            return max(0.1, min(3.0, float(retry_after)))
        except (TypeError, ValueError):
            return float(2**attempt)

    def _get_cached(self, key: str) -> PlayerStats | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.monotonic():
            self._cache.pop(key, None)
            return None
        self._cache.move_to_end(key)
        return entry.value

    def _set_cached(self, key: str, value: PlayerStats) -> None:
        now = time.monotonic()
        expired = [
            cache_key
            for cache_key, entry in self._cache.items()
            if entry.expires_at <= now
        ]
        for cache_key in expired:
            self._cache.pop(cache_key, None)

        self._cache[key] = _CacheEntry(value, now + self.cache_ttl)
        self._cache.move_to_end(key)
        while len(self._cache) > self.max_cache_entries:
            self._cache.popitem(last=False)
