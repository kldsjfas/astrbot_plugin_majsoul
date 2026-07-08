from dataclasses import dataclass
from math import isfinite
from typing import Any

MAJOR_RANKS = ("初心", "雀士", "雀杰", "雀豪", "雀圣", "魂天")


class DataFormatError(ValueError):
    """Raised when the remote API returns an unexpected payload."""


def _number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise DataFormatError(f"Invalid {field}") from exc
    if not isfinite(number):
        raise DataFormatError(f"Invalid {field}")
    return number


def _rate(value: Any, field: str) -> float:
    rate = _number(value, field)
    if not 0.0 <= rate <= 1.0:
        raise DataFormatError(f"Invalid {field}")
    return rate


def _optional_rate(value: Any) -> float | None:
    if value is None:
        return None
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return None
    return rate if isfinite(rate) and 0.0 <= rate <= 1.0 else None


def _optional_int(value: Any) -> int | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if isfinite(number) else None


def decode_level(level_id: Any) -> str:
    """Turn an amae-koromo level id (e.g. 10301) into a readable rank name."""
    try:
        code = int(level_id)
    except (TypeError, ValueError):
        return ""
    real = code % 10000
    major = real // 100
    minor = real % 100
    if not 1 <= major <= len(MAJOR_RANKS):
        return ""
    name = MAJOR_RANKS[major - 1]
    if major >= len(MAJOR_RANKS):  # 魂天没有细分段位
        return name
    return f"{name}{minor}" if minor else name


def _level_name_from(payload: Any) -> str:
    if isinstance(payload, dict):
        return decode_level(payload.get("id"))
    return decode_level(payload)


@dataclass(frozen=True, slots=True)
class PlayerCandidate:
    account_id: int | str
    nickname: str

    @classmethod
    def from_payload(cls, payload: Any) -> "PlayerCandidate":
        if not isinstance(payload, dict):
            raise DataFormatError("Invalid player payload")
        account_id = payload.get("id")
        nickname = payload.get("nickname")
        if account_id is None or not isinstance(nickname, str) or not nickname.strip():
            raise DataFormatError("Invalid player payload")
        return cls(account_id=account_id, nickname=nickname.strip())


@dataclass(frozen=True, slots=True)
class PlayerStats:
    nickname: str
    count: int
    rank_rates: tuple[float, ...]
    avg_rank: float
    deal_in_rate: float
    three_player: bool = False
    level_name: str = ""
    max_level_name: str = ""
    win_rate: float | None = None
    riichi_rate: float | None = None
    call_rate: float | None = None
    tsumo_rate: float | None = None
    avg_win_score: int | None = None
    max_renchan: int | None = None

    @property
    def seats(self) -> int:
        return 3 if self.three_player else 4

    @classmethod
    def from_payloads(
        cls,
        nickname: str,
        base: Any,
        extended: Any,
        *,
        three_player: bool = False,
    ) -> "PlayerStats":
        if not isinstance(base, dict):
            raise DataFormatError("Invalid statistics payload")
        seats = 3 if three_player else 4

        if "count" not in base or "rank_rates" not in base or "avg_rank" not in base:
            raise DataFormatError("Incomplete statistics payload")
        count = int(_number(base.get("count", 0), "count"))
        if count < 0:
            raise DataFormatError("Invalid count")

        ranks = base.get("rank_rates")
        if not isinstance(ranks, list) or len(ranks) < seats:
            raise DataFormatError("Invalid rank_rates")
        avg_rank = _number(base.get("avg_rank"), "avg_rank")
        if not 1.0 <= avg_rank <= float(seats):
            raise DataFormatError("Invalid avg_rank")

        ext = extended if isinstance(extended, dict) else {}
        deal_in = _optional_rate(ext.get("放铳率"))
        if deal_in is None:
            raise DataFormatError("Invalid deal_in_rate")

        return cls(
            nickname=nickname,
            count=count,
            rank_rates=tuple(
                _rate(ranks[index], f"rank_rates[{index}]") for index in range(seats)
            ),
            avg_rank=avg_rank,
            deal_in_rate=deal_in,
            three_player=three_player,
            level_name=_level_name_from(base.get("level")),
            max_level_name=_level_name_from(base.get("max_level")),
            win_rate=_optional_rate(ext.get("和牌率")),
            riichi_rate=_optional_rate(ext.get("立直率")),
            call_rate=_optional_rate(ext.get("副露率")),
            tsumo_rate=_optional_rate(ext.get("自摸率")),
            avg_win_score=_optional_int(ext.get("平均打点")),
            max_renchan=_optional_int(ext.get("最大连庄")),
        )

    def to_dict(self) -> dict[str, str | int]:
        rank_labels = ("一位率", "二位率", "三位率", "四位率")
        data: dict[str, str | int] = {
            "玩家": self.nickname,
            "模式": "三麻" if self.three_player else "四麻",
            "对局数": self.count,
        }
        if self.level_name:
            data["段位"] = self.level_name
        if self.max_level_name and self.max_level_name != self.level_name:
            data["最高段位"] = self.max_level_name
        for index in range(self.seats):
            data[rank_labels[index]] = f"{self.rank_rates[index] * 100:.2f}%"
        data["平均顺位"] = f"{self.avg_rank:.2f}"
        data["放铳率"] = f"{self.deal_in_rate * 100:.2f}%"
        if self.win_rate is not None:
            data["和牌率"] = f"{self.win_rate * 100:.2f}%"
        if self.riichi_rate is not None:
            data["立直率"] = f"{self.riichi_rate * 100:.2f}%"
        if self.call_rate is not None:
            data["副露率"] = f"{self.call_rate * 100:.2f}%"
        if self.tsumo_rate is not None:
            data["自摸率"] = f"{self.tsumo_rate * 100:.2f}%"
        if self.avg_win_score is not None:
            data["平均打点"] = self.avg_win_score
        if self.max_renchan is not None:
            data["最大连庄"] = self.max_renchan
        return data

    def to_text(self) -> str:
        mode = "三麻" if self.three_player else "四麻"
        title = f"【雀魂{mode}战绩】{self.nickname}"
        if self.level_name:
            title += f"　{self.level_name}"

        ranks = "　".join(
            f"{label}：{self.rank_rates[index] * 100:.2f}%"
            for index, label in enumerate(
                ("一位", "二位", "三位", "四位")[: self.seats]
            )
        )

        lines = [
            title,
            f"对局：{self.count} 场　平均顺位：{self.avg_rank:.2f}",
            ranks,
        ]

        detail = [f"放铳率：{self.deal_in_rate * 100:.2f}%"]
        if self.win_rate is not None:
            detail.append(f"和牌率：{self.win_rate * 100:.2f}%")
        if self.riichi_rate is not None:
            detail.append(f"立直率：{self.riichi_rate * 100:.2f}%")
        if self.call_rate is not None:
            detail.append(f"副露率：{self.call_rate * 100:.2f}%")
        lines.append("　".join(detail))

        tail = []
        if self.avg_win_score is not None:
            tail.append(f"平均打点：{self.avg_win_score}")
        if self.max_renchan is not None:
            tail.append(f"最大连庄：{self.max_renchan}")
        if tail:
            lines.append("　".join(tail))

        return "\n".join(lines)
