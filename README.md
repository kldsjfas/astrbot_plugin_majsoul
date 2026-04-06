<div align="center">


# 🀄 AstrBot Plugin: Majsoul

🌸 **专属日麻赛博算命与毒舌战绩教练（AI版）** 🌸

[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue)](https://github.com/Soulter/AstrBot)
[![License](https://img.shields.io/badge/License-AGPL%203.0-green.svg)](https://opensource.org/licenses/AGPL-3.0)


</div>

## ✨ 插件简介

这是一款为 [AstrBot](https://github.com/Soulter/AstrBot) 机器人开发的轻量化雀魂查谱吐槽插件。

它可以精准抓取玩家的战绩数据（一位率、放铳率等），或解析雀魂牌谱链接。AI 将根据这些冰冷的数据，化身傲娇教练对你一顿“猫嘴锐评”，或者化身赛博算命大师吐槽你的稀烂防守！

## 🚀 指令与触发方式

当本插件启用后，用户可以直接对机器人提及以下指令：

| 触发方式 | 说明 | 参数解释 |
| :--- | :--- | :--- |
| **聊天提及** `"查雀魂 [昵称]"` | 触发 AI 工具，查询目标玩家战绩并进行毒舌点评。 | `[昵称]`: 目标玩家的游戏名字 |
| **发送牌谱链接** | 包含 `game.maj-soul.com/1/?paipu=` 的链接 | 触发 AI 工具，AI 将化身算命大师吐槽这局牌。 |
| **纯文本指令** `/查谱 [ID/链接]` | (规划中) 手动触发牌谱分析，无 AI 介入的纯数据模式。 | `[ID/链接]`: 牌谱ID或完整链接 |

## ⚙️ 配置面板

本插件支持在 AstrBot 的 WebUI 管理后台进行可视化配置：

| 配置项 | 类型 | 默认值 | 说明 |
| :--- | :---: | :---: | :--- |
| **内置教练人格** | `下拉栏` | 傲娇毒舌 | 提供多种内置的日麻专属吐槽人格供随时切换。 |
| **赛博火力值** | `数字` | 3 | 设定吐槽的猛烈程度 (1-3级)，3级为火力全开！ |
| **覆盖开关：系统人格** | `开关` | 关 | 开启后将忽略下拉选择，强制使用 AstrBot 当前選中的全局人格进行点评。 |

## 📦 安装方法

直接在 AstrBot 的 WebUI 插件市场中搜索 `astrbot_plugin_majsoul` 进行一键安装。

## 📜 许可证

本项目基于 AGPL-3.0 协议开源。

</div>
