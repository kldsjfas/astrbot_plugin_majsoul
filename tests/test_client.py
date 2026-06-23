import asyncio

import pytest
from astrbot_plugin_majsoul.majsoul_client import (
    InvalidNickname,
    MajsoulApiClient,
    MultiplePlayersFound,
    RemoteServiceError,
)

VALID_STATS = {
    "count": 50,
    "rank_rates": [0.25, 0.25, 0.25, 0.25],
    "deal_in_rate": 0.1,
    "avg_rank": 2.5,
}


class FakeClient(MajsoulApiClient):
    def __init__(self, responses):
        super().__init__(cache_ttl=600, max_cache_entries=2)
        self.responses = list(responses)
        self.calls = 0

    async def _request_json(self, url):
        self.calls += 1
        return self.responses.pop(0)


def test_query_prefers_exact_nickname_and_uses_cache():
    async def run():
        client = FakeClient(
            [
                [
                    {"id": 1, "nickname": "玩家甲"},
                    {"id": 2, "nickname": "目标玩家"},
                ],
                VALID_STATS,
            ]
        )
        first = await client.query_player("目标玩家")
        second = await client.query_player("目标玩家")
        assert first == second
        assert first.nickname == "目标玩家"
        assert client.calls == 2

    asyncio.run(run())


def test_query_reports_ambiguous_partial_nickname():
    async def run():
        client = FakeClient(
            [[{"id": 1, "nickname": "玩家甲"}, {"id": 2, "nickname": "玩家乙"}]]
        )
        with pytest.raises(MultiplePlayersFound) as exc_info:
            await client.query_player("玩家")
        assert exc_info.value.candidates == ("玩家甲", "玩家乙")

    asyncio.run(run())


def test_query_rejects_empty_and_oversized_nicknames():
    async def run():
        client = FakeClient([])
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
        client = SlowClient([[{"id": 1, "nickname": "同一玩家"}], VALID_STATS])
        results = await asyncio.gather(
            client.query_player("同一玩家"), client.query_player("同一玩家")
        )
        assert results[0] == results[1]
        assert client.calls == 2

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
