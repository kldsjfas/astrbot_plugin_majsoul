<div align="center">

<div align="center">
  <img src="https://count.getloli.com/get/@killer_qert_majsoul?theme=moebooru" width="900" alt="猫娘计数器" />
</div>

# 🀄 AstrBot Plugin: Majsoul

[![License](https://img.shields.io/badge/License-AGPL%203.0-green.svg)](https://opensource.org/licenses/AGPL-3.0)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot-4.25+-red.svg)](https://github.com/AstrBotDevs/AstrBot)
[![Author](https://img.shields.io/badge/作者-killer--qert-orange.svg)](https://github.com/kldsjfas)

</div>


## ✨ 插件简介

这是个给 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 用的雀魂战绩查询插件。最开始只是想让机器人帮忙查查数据，顺便吐槽两句，后来就慢慢补到了现在。

目前可以查询玩家的公开四麻战绩，包括一位率、放铳率、平均顺位这些常用数据，查完也可以交给 AI 做个简单点评。牌谱部分暂时只能识别链接和牌谱 ID，还不能真的复盘每一巡，这里先说清楚，免得大家以为它已经会看完整牌谱了。

## 🚀 指令与触发方式

插件启用后，可以直接使用下面这些指令：

| 触发方式 | 说明 | 参数解释 |
| :--- | :--- | :--- |
| **聊天提及** `"查雀魂 [昵称]"` | 让 AI 查询目标玩家的公开战绩并进行点评。 | `[昵称]`：玩家的完整游戏昵称 |
| **纯文本指令** `/查雀魂 [昵称]` | 直接查询公开四麻战绩，不需要等 AI 判断。 | `[昵称]`：玩家的完整游戏昵称 |
| **纯文本指令** `/查谱 [ID/链接]` | 从雀魂牌谱链接中提取牌谱 ID。 | `[ID/链接]`：牌谱 ID 或完整链接 |
| **纯文本指令** `/雀魂帮助` | 查看插件现有指令和注意事项。 | 不需要参数 |

## ⚙️ 配置面板

插件支持在 AstrBot 的 WebUI 管理后台里调整配置。第一次用的话保持默认就行，不用每项都改。

| 配置项 | 类型 | 默认值 | 说明 |
| :--- | :---: | :---: | :--- |
| **使用系统人格** | `开关` | 关 | 开启后使用 AstrBot 当前选择的系统人格来点评。 |
| **插件内置人格** | `下拉栏` | 傲娇毒舌教练 | 不使用系统人格时，选择插件自己的点评风格。 |
| **吐槽强度** | `数字` | 3 | 范围 1-3，数字越大说话越不客气。 |
| **请求超时** | `数字` | 15 秒 | 外部战绩接口多久没响应就停止等待。 |
| **缓存时间** | `数字` | 600 秒 | 同一个玩家的战绩在本地保留多久。 |
| **缓存人数** | `数字` | 256 | 最多缓存多少名玩家的数据。 |

## 📦 安装方法

直接在 AstrBot 的 WebUI 插件市场里搜索 `astrbot_plugin_majsoul` 安装即可。

也可以在插件管理页填写仓库地址安装：

`https://github.com/kldsjfas/astrbot_plugin_majsoul`

## 🛠️ 2.0.0 更新

- 适配 AstrBot 4.25.6 和 Python 3.12。
- 重写战绩查询流程，补上超时、重试、缓存和更清楚的报错。
- 增加 `/查雀魂`、`/查谱`、`/雀魂帮助` 三个指令。
- 玩家重名时不再随便取第一个结果，会提示输入完整昵称。
- 修了一些链接识别、数据缺失和插件退出时资源没有释放的问题。
- 加了自动检查，目前一共有 15 个测试。

更完整的更新记录可以看 [CHANGELOG.md](CHANGELOG.md)。

## 开发者碎碎念

本人是编程萌新兼大学生，这个插件本来就是兴趣使然的练手项目。代码不一定写得多漂亮，不过能修的 Bug 我会尽量修，有问题可以直接去仓库里提。

## 📜 许可证

本项目基于 AGPL-3.0 协议开源。

</div>
