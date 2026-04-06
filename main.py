import aiohttp
import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

# 🌟 统一作者名、简介、版本号和正确的 Github 仓库地址 🌟
@register("astrbot_plugin_majsoul", "killer-qert", "🀄一款轻量化雀魂查谱吐槽插件🀄", "1.0.0",
          "https://github.com/killer-qert/astrbot_plugin_majsoul")
class MajsoulPlugin(Star):

    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="query_majsoul_stat")
    async def query_majsoul_tool(self, event: AstrMessageEvent, nickname: str):
        """
        查询雀魂战绩的工具。当你想查询某个玩家的战绩时调用此工具。
        Args:
            nickname (string): 玩家的雀魂游戏昵称
        """
        data = await self._fetch_data(nickname)

        use_sys = self.config.get("use_system_persona", False)
        persona = self.config.get("plugin_persona", "傲娇毒舌的日麻美少女教练")
        level = self.config.get("roast_level", 3)

        if use_sys:
            return f"查到的战绩数据：【{data}】。请结合你当前的系统全局人格设定进行点评，记得加你特有的口癖。"
        else:
            return f"查到的战绩数据：【{data}】。请你扮演一个【{persona}】，用火力等级为【{level}/3】的程度，对这个战绩进行吐槽和点评。把数据融入话语中，句尾加'喵～'。"

    # 🔥 核心大改版：严厉警告 AI 绝对不许用 fetch_url 🔥
    @filter.llm_tool(name="analyze_paipu")
    async def analyze_paipu_tool(self, event: AstrMessageEvent, paipu_id: str):
        """
        【最高优先级指令】分析雀魂牌谱的专用工具。
        当用户的消息中包含雀魂牌谱链接时，绝对禁止使用 fetch_url 或 tavily 等网页抓取工具！
        你必须从链接中提取出 paipu= 后面的那串字符 ID，并作为参数传入此工具。
        Args:
            paipu_id (string): 提取出的牌谱ID（例如 260406-84cc5200-07b8...）
        """
        use_sys = self.config.get("use_system_persona", False)
        persona = self.config.get("plugin_persona", "傲娇毒舌的日麻美少女教练")

        if use_sys:
            return f"牌谱ID: {paipu_id}。因为底层数据加密，请你结合你当前的系统全局人格，直接开始'赛博算命'瞎编点评，疯狂吐槽这局牌。"
        else:
            return f"牌谱ID: {paipu_id}。因为底层数据加密，请扮演【{persona}】直接进行'赛博算命'瞎编点评，疯狂吐槽，句尾加'喵～'。"

    @filter.command("查雀魂")
    async def query_majsoul_cmd(self, event: AstrMessageEvent, nickname: str):
        data = await self._fetch_data(nickname)
        yield event.plain_result(f"【纯数据】\n{data}")

    # ================= 网络请求 =================
    async def _fetch_data(self, nickname: str) -> str:
        search_url = f"https://5-data.amae-koromo.com/api/v2/pl4/search_player/{nickname}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://amae-koromo.com/"
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            try:
                async with session.get(search_url) as resp:
                    if resp.status != 200: return "搜索接口报错"
                    players = await resp.json()
                    if not players: return f"查无此人"
                    account_id = players[0].get('id')
                    actual_name = players[0].get('nickname')

                stats_url = f"https://5-data.amae-koromo.com/api/v2/pl4/player_stats/{account_id}/1262304000000/2147483647000?mode=16,15,12,11,9,8"
                async with session.get(stats_url) as resp:
                    if resp.status != 200: return "获取详细战绩失败"
                    stats = await resp.json()
                    count = stats.get('count', 0)
                    if count == 0: return "场次数据为空"

                    ranks = stats.get('rank_rates', [0, 0, 0, 0])
                    first_rate = ranks[0] * 100 if len(ranks) > 0 else 0
                    deal_in_rate = stats.get('deal_in_rate', 0) * 100
                    avg_rank = stats.get('avg_rank', 0)
                    return f"玩家：{actual_name}，对局：{count}场，一位率：{first_rate:.2f}%，放铳率：{deal_in_rate:.2f}%，平均顺位：{avg_rank:.2f}"
            except Exception as e:
                logger.error(f"报错: {e}")
                return "代码发生意外故障"