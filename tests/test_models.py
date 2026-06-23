import pytest
from astrbot_plugin_majsoul.models import DataFormatError, PlayerStats


def test_player_stats_parses_and_formats_all_rank_rates():
    stats = PlayerStats.from_payload(
        "测试玩家",
        {
            "count": 100,
            "rank_rates": [0.3, 0.25, 0.25, 0.2],
            "deal_in_rate": 0.12,
            "avg_rank": 2.35,
        },
    )

    assert stats.to_dict()["四位率"] == "20.00%"
    assert "平均顺位：2.35" in stats.to_text()
    assert "放铳率：12.00%" in stats.to_text()


def test_player_stats_rejects_incomplete_rank_rates():
    with pytest.raises(DataFormatError):
        PlayerStats.from_payload(
            "测试玩家",
            {"count": 10, "rank_rates": [0.5], "deal_in_rate": 0.1, "avg_rank": 2},
        )


def test_player_stats_rejects_invalid_ranges():
    with pytest.raises(DataFormatError):
        PlayerStats.from_payload(
            "测试玩家",
            {
                "count": -5,
                "rank_rates": [2, -1, 0.2, 0.3],
                "deal_in_rate": 4,
                "avg_rank": 9,
            },
        )


def test_player_stats_rejects_missing_fields():
    with pytest.raises(DataFormatError):
        PlayerStats.from_payload(
            "测试玩家",
            {"count": 10, "rank_rates": [0.25, 0.25, 0.25, 0.25]},
        )
