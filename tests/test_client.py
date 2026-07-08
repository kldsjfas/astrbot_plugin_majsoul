import asyncio

import pytest
from astrbot_plugin_majsoul.majsoul_client import (
    InvalidNickname,
    MajsoulApiClient,
    MultiplePlayersFound,
    RemoteServiceError,
)


def _base_stats(seats=4):
    return {
        "count": 50,
        "rank_rates": [round(1 / seats, 4)] * seats,
        "avg_rank": (seats + 1) / 2,
        "level": {"id": 10301},
        "max_level": {"id": 10401},
    }


def _ext_stats():
    return {
        "count": 50,
        "放铳率": 0.1,
        "和牌率": 0.2,
        "立直率": 0.18,
        "副露率": 0.3,
        "自摸率": 0.35,
        "平均打点": 4600,
        "最大连庄": 2,
    }


class FakeClient(MajsoulApiClient):
    """Route fake responses by URL so 三麻/四麻 and both stat endpoints work."""

    def __init__(self, *, search=None, seats=4):
        super().__init__(cache_ttl=600, max_cache_entries=2)
        self.search = search
        self.seats = seats
        self.calls = 0

    async def _request_json(self, url):
        self.calls += 1
        if "search_player" in url:
            if self.search is None:
                raise AssertionError("unexpected search call")
            return self.search
        if "player_extended_stats" in url:
            return _ext_stats()
        if "player_stats" in url:
            return _base_stats(self.seats)
        raise AssertionError(f"unexpected url: {url}")


def test_query_prefers_exact_nickname_and_uses_cache():
    async def run():
        client = FakeClient(
            search=[
                {"id": 1, "nickname": "玩家甲"},
                {"id": 2, "nickname": "目标玩家"},
            ]
        )
        first = await client.query_player("目标玩家")
        second = await client.query_player("目标玩家")
        assert first == second
        assert first.nickname == "目标玩家"
        assert first.deal_in_rate == 0.1
        assert first.win_rate == 0.2
        assert client.calls == 3  # search + player_stats + extended_stats

    asyncio.run(run())


def test_query_three_player_uses_pl3_and_three_ranks():
    async def run():
        client = FakeClient(search=[{"id": 3, "nickname": "三麻玩家"}], seats=3)
        stats = await client.query_player("三麻玩家", three_player=True)
        assert stats.three_player is True
        assert stats.seats == 3
        assert len(stats.rank_rates) == 3
        assert "三麻" in stats.to_text()

    asyncio.run(run())


def test_query_reports_ambiguous_partial_nickname():
    async def run():
        client = FakeClient(
            search=[{"id": 1, "nickname": "玩家甲"}, {"id": 2, "nickname": "玩家乙"}]
        )
        with pytest.raises(MultiplePlayersFound) as exc_info:
            await client.query_player("玩家")
        assert exc_info.value.candidates == ("玩家甲", "玩家乙")

    asyncio.run(run())


def test_query_rejects_empty_and_oversized_nicknames():
    async def run():
        client = FakeClient()
        with pytest.raises(InvalidNickname):
            await client.query_player(" ")
        with pytest.raises(InvalidNickname):
            await client.query_player("x" * 65)

    asyncio.run(run())


def test_concurrent_queries_share_one_request():
    class SlowClient(FakeClient):
        async def _request_json(self, url):
            await asyncio.sleep(0.01)
            return await super()._request_json(url)

    async def run():
        client = SlowClient(search=[{"id": 1, "nickname": "同一玩家"}])
        results = await asyncio.gather(
            client.query_player("同一玩家"), client.query_player("同一玩家")
        )
        assert results[0] == results[1]
        assert client.calls == 3

    asyncio.run(run())


class FakeResponse:
    def __init__(self, status, payload=None, headers=None):
        self.status = status
        self.payload = payload
        self.headers = headers or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def json(self, content_type=None):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.closed = False
        self.calls = 0

    def get(self, url):
        self.calls += 1
        return self.responses.pop(0)

    async def close(self):
        self.closed = True


def test_request_retries_temporary_server_error():
    async def run():
        client = MajsoulApiClient()
        session = FakeSession([FakeResponse(503), FakeResponse(200, {"status": "ok"})])
        client._session = session
        client._retry_delay = lambda attempt, retry_after="": 0
        assert await client._request_json("https://example.invalid") == {"status": "ok"}
        assert session.calls == 2

    asyncio.run(run())


def test_request_does_not_retry_client_error():
    async def run():
        client = MajsoulApiClient()
        session = FakeSession([FakeResponse(400)])
        client._session = session
        with pytest.raises(RemoteServiceError):
            await client._request_json("https://example.invalid")
        assert session.calls == 1

    asyncio.run(run())
