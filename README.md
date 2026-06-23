# 雀魂 Majsoul 助手

一个用于 AstrBot 的雀魂战绩查询插件。它通过公开接口查询玩家数据，也可以把战绩交给模型做简短点评。

## 环境要求

- AstrBot 4.25 或更高版本
- Python 3.12 或更高版本

## 使用方法

| 指令 | 作用 |
| --- | --- |
| `/查雀魂 <完整昵称>` | 查询公开战绩 |
| `/查谱 <链接或ID>` | 提取牌谱 ID |
| `/雀魂帮助` | 查看指令说明 |

也可以在正常对话中让模型查询某个玩家的雀魂战绩。查询成功后会提供四麻的一至四位率、放铳率和平均顺位。

## 配置

插件管理页面可以调整点评人格、吐槽强度、请求超时和缓存时间。一般保持默认值即可。

## 说明

- 战绩来自 `amae-koromo.com` 的公开接口，接口异常时插件会重试并返回明确提示。
- 查询接口可能只收录部分段位或模式，完整昵称也可能查不到。
- 牌谱内容经过加密，本插件目前只识别牌谱 ID，不提供真实牌局解析。
- 插件不会读取雀魂账号、密码或登录凭据。

## 安装

在 AstrBot 插件市场搜索“雀魂 Majsoul 助手”，或在插件管理页面填写本仓库地址安装：

`https://github.com/kldsjfas/astrbot_plugin_majsoul`

## 开发检查

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff format --check .
ruff check .
pytest -q
```

更新内容见 [CHANGELOG.md](CHANGELOG.md)。

本项目使用 AGPL-3.0 许可证。
