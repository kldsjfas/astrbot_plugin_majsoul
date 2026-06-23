from dataclasses import dataclass
from math import isfinite
from typing import Any


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
    rank_rates: tuple[float, float, float, float]
    deal_in_rate: float
    avg_rank: float

    @classmethod
    def from_payload(cls, nickname: str, payload: Any) -> "PlayerStats":
        if not isinstance(payload, dict):
            raise DataFormatError("Invalid statistics payload")
        required = {"count", "rank_rates", "deal_in_rate", "avg_rank"}
        if not required.issubset(payload):
            raise DataFormatError("Incomplete statistics payload")

        count = int(_number(payload.get("count", 0), "count"))
        if count < 0:
            raise DataFormatError("Invalid count")
        ranks = payload.get("rank_rates")
        if not isinstance(ranks, list) or len(ranks) < 4:
            raise DataFormatError("Invalid rank_rates")
        avg_rank = _number(payload.get("avg_rank"), "avg_rank")
        if not 1.0 <= avg_rank <= 4.0:
            raise DataFormatError("Invalid avg_rank")

        return cls(
            nickname=nickname,
            count=count,
            rank_rates=tuple(
                _rate(ranks[index], f"rank_rates[{index}]") for index in range(4)
            ),
            deal_in_rate=_rate(payload.get("deal_in_rate", 0), "deal_in_rate"),
            avg_rank=avg_rank,
        )

    def to_dict(self) -> dict[str, str | int]:
        return {
            "玩家": self.nickname,
            "对局数": self.count,
            "一位率": f"{self.rank_rates[0] * 100:.2f}%",
            "二位率": f"{self.rank_rates[1] * 100:.2f}%",
            "三位率": f"{self.rank_rates[2] * 100:.2f}%",
            "四位率": f"{self.rank_rates[3] * 100:.2f}%",
            "放铳率": f"{self.deal_in_rate * 100:.2f}%",
            "平均顺位": f"{self.avg_rank:.2f}",
        }

    def to_text(self) -> str:
        data = self.to_dict()
        return (
            f"【雀魂战绩】{data['玩家']}\n"
            f"对局：{data['对局数']} 场　平均顺位：{data['平均顺位']}\n"
            f"一位：{data['一位率']}　二位：{data['二位率']}\n"
            f"三位：{data['三位率']}　四位：{data['四位率']}\n"
            f"放铳率：{data['放铳率']}"
        )
