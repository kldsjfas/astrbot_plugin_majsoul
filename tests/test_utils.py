from astrbot_plugin_majsoul.utils import bounded_int, clean_persona, extract_paipu_id


def test_extract_paipu_id_from_query_url():
    assert (
        extract_paipu_id("https://game.maj-soul.com/1/?paipu=260406-84cc5200-test_id")
        == "260406-84cc5200-test_id"
    )


def test_extract_paipu_id_from_raw_value():
    assert extract_paipu_id("260406-84cc5200-test_id") == "260406-84cc5200-test_id"


def test_extract_paipu_id_rejects_invalid_value():
    assert extract_paipu_id("不是牌谱") == ""
    assert extract_paipu_id("javascript:alert(1)") == ""


def test_bounded_int_uses_default_and_limits():
    assert bounded_int("bad", 15, 5, 30) == 15
    assert bounded_int(2, 15, 5, 30) == 5
    assert bounded_int(99, 15, 5, 30) == 30


def test_clean_persona_removes_line_breaks_and_limits_length():
    assert clean_persona("冷静\n分析", "默认") == "冷静 分析"
    assert len(clean_persona("x" * 200, "默认")) == 80
