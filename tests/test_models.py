import pytest
from astrbot_plugin_majsoul.models import DataFormatError, PlayerStats, decode_level

BASE = {
    "count": 100,
    "rank_rates": [0.3, 0.25, 0.25, 0.2],
    "avg_rank": 2.35,
    "level": {"id": 10301},
    "max_level": {"id": 10401},
}
EXT = {
    "放铳率": 0.12,
    "和牌率": 0.21,
    "立直率": 0.18,
    "副露率": 0.34,
    "平均打点": 4800,
    "最大连庄": 3,
}


def test_player_stats_parses_and_formats_all_rank_rates():
    stats = PlayerStats.from_payloads("测试玩家", BASE, EXT)

    assert stats.to_dict()["四位率"] == "20.00%"
    assert "平均顺位：2.35" in stats.to_text()
    assert "放铳率：12.00%" in stats.to_text()
    assert "和牌率：21.00%" in stats.to_text()


def test_player_stats_includes_level_and_extended_fields():
    stats = PlayerStats.from_payloads("测试玩家", BASE, EXT)

    assert stats.level_name == "雀杰1"
    assert stats.max_level_name == "雀豪1"
    assert stats.win_rate == 0.21
    assert stats.to_dict()["段位"] == "雀杰1"
    assert stats.to_dict()["平均打点"] == 4800


def test_three_player_stats_use_three_ranks():
    base = {
        "count": 40,
        "rank_rates": [0.4, 0.3, 0.3],
        "avg_rank": 1.9,
        "level": {"id": 20401},
    }
    stats = PlayerStats.from_payloads("三麻玩家", base, EXT, three_player=True)

    assert stats.seats == 3
    assert "四位" not in stats.to_text()
    assert "三麻" in stats.to_text()
    assert "四位率" not in stats.to_dict()


def test_decode_level_reads_major_and_minor():
    assert decode_level(10101) == "初心1"
    assert decode_level(10403) == "雀豪3"
    assert decode_level(10601) == "魂天"
    assert decode_level(20301) == "雀杰1"
    assert decode_level("bad") == ""


def test_player_stats_rejects_incomplete_rank_rates():
    with pytest.raises(DataFormatError):
        PlayerStats.from_payloads(
            "测试玩家",
            {"count": 10, "rank_rates": [0.5], "avg_rank": 2},
            EXT,
        )


def test_player_stats_rejects_invalid_ranges():
    with pytest.raises(DataFormatError):
        PlayerStats.from_payloads(
            "测试玩家",
            {"count": -5, "rank_rates": [2, -1, 0.2, 0.3], "avg_rank": 9},
            EXT,
        )


def test_player_stats_requires_deal_in_rate_from_extended():
    with pytest.raises(DataFormatError):
        PlayerStats.from_payloads("测试玩家", BASE, {})
