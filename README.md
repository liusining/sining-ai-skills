# Sining AI Skills

为我的 AI Agent 编写的技能（Skills）合集。

## 技能列表

| 技能 | 说明 |
|------|------|
| [snell-surge-deploy](snell-surge-deploy/) | 在远程 Linux VPS 上部署 Snell 服务器，并自动配置本地 Surge 客户端的代理条目。 |

## OpenClaw 专用技能

以下技能仅适用于 [OpenClaw](https://openclaw.com)，不适用于 Claude Code。

| 技能 | 说明 |
|------|------|
| [skill-install](openclaw/skill-install/) | 安装、添加或更新 OpenClaw 技能。支持从 ClawHub、GitHub 或本地路径安装，内置安全扫描流程。 |
| [weflow-group-summarizer](openclaw/weflow-group-summarizer/) | 设置微信群聊监控，通过 WeFlow API 定期抓取群消息并生成摘要总结。 |

## 在 Claude Code 中安装技能

本仓库的通用技能可以作为 Claude Code 插件安装。`openclaw/` 目录下的技能不会被 Claude Code 发现或安装。

### 添加 Marketplace 并安装

在 Claude Code 会话中执行以下斜杠命令：

```
# 1. 添加本仓库为第三方 marketplace
/plugin marketplace add liusining/sining-ai-skills

# 2. 查看可用插件和 marketplace 名称
/plugin marketplace list

# 3. 安装插件（替换为实际的插件名和 marketplace 名称）
/plugin install <plugin-name>@<marketplace-name>
```

### 关于 openclaw 目录

`openclaw/` 下的技能专为 OpenClaw 平台设计。Claude Code 的插件系统通过 `.claude-plugin/marketplace.json` 显式注册可用插件——只有在 marketplace.json 中列出的插件才会被发现和安装。`openclaw/` 目录下的技能不在此列表中，因此不会被 Claude Code 安装。
